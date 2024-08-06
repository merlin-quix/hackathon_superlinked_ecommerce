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
    Defines a data schema for product information. It includes fields for description,
    name, category, price, review count, and rating, as well as an ID field. This
    schema outlines the structure and type of data for each product attribute.

    Attributes:
        description (String): Mandatory as it has no default value assigned. It
            represents a description of the product.
        name (String): Required to hold a name for the product. It can be any
            string value, without any specific length or format restriction.
        category (String): Described as a category of the product, likely representing
            a broad or narrow classification within a product hierarchy.
        price (Integer): Represented as a whole number with no decimal places,
            indicating the monetary value of a product.
        review_count (Integer): Intended to store the count of reviews for a product.
        review_rating (Integer): A representation of the average rating given by
            customers for a product based on their reviews.
        id (IdField): Part of the schema for products. It represents a unique
            identifier for each product, likely used to identify or link to specific
            products within the system.

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
    Defines a schema for user preferences, comprising four fields: `preference_description`,
    `preference_name`, `preference_category`, and `id`. This schema provides a
    structured format for storing and managing user preferences.

    Attributes:
        preference_description (String): Used to describe a user's preference.
        preference_name (String): Part of the schema definition for user preferences.
            It likely represents a descriptive name or label for a user's preference,
            such as "Favorite Color" or "Preferred Language".
        preference_category (String): Part of a user's preferences, likely
            categorizing their specific preference (e.g., music genre).
        id (IdField): A unique identifier for each user object.

    """
    preference_description: String
    preference_name: String
    preference_category: String
    id: IdField

@event_schema
class EventSchema:
    """
    Defines a schema for representing events, which can be products or user-related
    actions. It contains fields for product and user references, event type, unique
    ID, and creation timestamp. This schema provides structure for storing and
    querying events in a database or API response.

    Attributes:
        product (SchemaReference[ProductSchema]): Referenced from another schema,
            indicating that it represents a reference to a ProductSchema object.
        user (SchemaReference[UserSchema]): Referenced from a UserSchema.
        event_type (String): Part of the schema definition for events. It represents
            the type of event being recorded.
        id (IdField): Implicitly considered as a unique identifier for each event
            instance, allowing it to be uniquely identified and referenced throughout
            the system.
        created_at (CreatedAtField): Expected to be present in all instances of
            this schema. Its presence suggests that it stores information related
            to when the event was created, likely as a timestamp.

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

redis_vector_database = RedisVectorDatabase("redis-18118.c328.europe-west3-1.gce.cloud.redislabs.com", 18118, username="default", password="*****")

executor = RestExecutor(
    sources=[source_product, source_user, source_event],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=redis_vector_database,
)

SuperlinkedRegistry.register(executor)
