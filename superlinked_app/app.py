from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.embedding.number_embedding import Mode
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.event_schema import event_schema
from superlinked.framework.common.schema.schema_object import String, Integer
from superlinked.framework.common.schema.event_schema_object import (
    CreatedAtField,
    SchemaReference,
)
from superlinked.framework.dsl.executor.rest.rest_configuration import (
    RestQuery,
)
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.index.effect import Effect
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace
from superlinked.framework.dsl.space.number_space import NumberSpace
from superlinked.framework.dsl.storage.redis_vector_database import RedisVectorDatabase


# Define schemas
@schema
class ProductSchema:
    """
    Defines a schema for product data, specifying attributes such as description,
    name, category, price, review count and rating, and an ID.

    Attributes:
        description (String): Required for a product's description. It can hold
            any text data about the product, providing more information to customers
            before they make a purchase.
        name (String): Required for product objects, representing the name or title
            of a product.
        category (String): A characteristic or classification of the product, which
            represents its grouping within a product hierarchy.
        price (Integer): A numerical value representing the cost of a product.
        review_count (Integer): A count of reviews for a product.
        review_rating (Integer): Part of the product schema definition, representing
            the average rating given by customers to a particular product based
            on the number of reviews received.
        id (IdField): Designated to uniquely identify a product instance.

    """
    description: String
    name: String
    category: String
    price: Integer
    review_count: Integer
    review_rating: Integer
    id: IdField

@schema
class UserSchema:
    """
    Defines a data model for user preferences, comprising four attributes:
    `preference_description`, `preference_name`, `preference_category`, and `id`.
    It represents a structured representation of user preferences, enabling efficient
    storage and retrieval.

    Attributes:
        preference_description (String): Part of the schema for a user's preferences.
            It represents a brief description of the preference.
        preference_name (String): Part of the schema definition for a user entity.
            It represents the name of a user's preference.
        preference_category (String): A field within the schema that represents a
            category for user preferences.
        id (IdField): Part of the UserSchema definition. It represents a unique
            identifier for each user in the system.

    """
    preference_description: String
    preference_name: String
    preference_category: String
    id: IdField

@event_schema
class EventSchema:
    """
    Defines a data structure for events, comprising references to product and user
    schemas, an event type, and three fields for storing unique identifiers and
    timestamps: `id`, `created_at`.

    Attributes:
        product (SchemaReference[ProductSchema]): Referenced to a ProductSchema.
        user (SchemaReference[UserSchema]): Referenced from the UserSchema.
        event_type (String): A part of the schema definition for events. It
            represents the type of event being described, allowing for categorization
            and organization of different types of events.
        id (IdField): Not further defined in this snippet. It likely represents a
            unique identifier for each event.
        created_at (CreatedAtField): Not further defined. It likely represents a
            timestamp indicating when the event was created.

    """
    product: SchemaReference[ProductSchema]
    user: SchemaReference[UserSchema]
    event_type: String
    id: IdField
    created_at: CreatedAtField


# Instantiate schemas
product_schema = ProductSchema()
user_schema = UserSchema()
event_schema = EventSchema()

# Define spaces
description_space = TextSimilaritySpace(
    text=[user_schema.preference_description, product_schema.description],
    model="sentence-transformers/all-distilroberta-v1",
)
name_space = TextSimilaritySpace(
    text=[user_schema.preference_name, product_schema.name],
    model="sentence-transformers/all-distilroberta-v1",
)
category_space = TextSimilaritySpace(
    text=[user_schema.preference_category, product_schema.category],
    model="sentence-transformers/all-distilroberta-v1",
)
price_space = NumberSpace(
    number=product_schema.price, mode=Mode.MINIMUM, min_value=25, max_value=1000
)
review_count_space = NumberSpace(
    number=product_schema.review_count, mode=Mode.MAXIMUM, min_value=0, max_value=100
)
review_rating_space = NumberSpace(
    number=product_schema.review_rating, mode=Mode.MAXIMUM, min_value=0, max_value=4
)

# Define event weights
event_weights = {
    "clicked_on": 0.2,
    "buy": 1,
    "put_to_cart": 0.5,
    "removed_from_cart": -0.5,
}

index = Index(
    spaces=[
        description_space,
        category_space,
        name_space,
        price_space,
        review_count_space,
        review_rating_space,
    ],
    effects=[
        Effect(
            description_space,
            event_schema.user,
            event_weight * event_schema.product,
            event_schema.event_type == event_type,
        )
        for event_type, event_weight in event_weights.items()
    ]
    + [
        Effect(
            category_space,
            event_schema.user,
            event_weight * event_schema.product,
            event_schema.event_type == event_type,
        )
        for event_type, event_weight in event_weights.items()
    ]
    + [
        Effect(
            name_space,
            event_schema.user,
            event_weight * event_schema.product,
            event_schema.event_type == event_type,
        )
        for event_type, event_weight in event_weights.items()
    ],
)


query = (
    Query(
        index,
        weights={
            description_space: Param("description_weight"),
            category_space: Param("category_weight"),
            name_space: Param("name_weight"),
            price_space: Param("price_weight"),
            review_count_space: Param("review_count_weight"),
            review_rating_space: Param("review_rating_weight"),
        },
    )
    .find(product_schema)
    .with_vector(user_schema, Param("user_id"))
    .limit(Param("limit"))
)

# Define Sources
source_product: RestSource = RestSource(product_schema)
source_user: RestSource = RestSource(user_schema)
source_event: RestSource = RestSource(event_schema)

redis_vector_database = RedisVectorDatabase("redis-18118.c328.europe-west3-1.gce.cloud.redislabs.com", 18118, username="default", password="7InsdOKm3MoA4SDplFF7DVEEf0bTlkud")

executor = RestExecutor(
    sources=[source_product, source_user, source_event],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=redis_vector_database,
)

SuperlinkedRegistry.register(executor)
