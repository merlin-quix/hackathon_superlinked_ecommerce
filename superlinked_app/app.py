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
    Defines a data structure for representing product information, including
    description, name, category, price, number of reviews, average rating, and
    unique identifier. This schema enables structured data storage and retrieval
    for products in an application.

    Attributes:
        description (String): Optional, as it does not have any additional
            specifications such as uniqueness or default values defined.
        name (String): Required for a product, representing its identifying name
            or title.
        category (String): Used to store a category name or label for each product,
            representing its classification or grouping within a larger hierarchy.
        price (Integer): Representative of a product's price.
        review_count (Integer): Part of a product's schema. It likely represents
            the total number of reviews received by that product, providing
            information about its popularity or user engagement.
        review_rating (Integer): A measure of the overall rating given by customers
            to the product, typically on a scale of 1-5 or 1-10.
        id (IdField): Intended to store a unique identifier for each product instance.

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
    Defines a schema for user preferences, consisting of four fields:
    `preference_description`, `preference_name`, `preference_category`, and `id`.
    The `id` field is specifically designated as an `IdField`, implying it serves
    as the unique identifier for each user preference.

    Attributes:
        preference_description (String): Named as `preference_description`. It
            appears to represent a descriptive text related to user preferences.
        preference_name (String): Part of the schema definition. It represents a
            named preference of a user, possibly used to categorize or identify
            specific preferences.
        preference_category (String): A property that represents the category of
            a user's preference.
        id (IdField): Represented by the keyword `id`. It is a unique identifier
            for each user.

    """
    preference_description: String
    preference_name: String
    preference_category: String
    id: IdField

@event_schema
class EventSchema:
    """
    Defines a schema for an event, which consists of four parts: a product, a user,
    an event type, and an ID and creation time stamp. The event is structured using
    other predefined schemas (`ProductSchema` and `UserSchema`).

    Attributes:
        product (SchemaReference[ProductSchema]): Referenced from a schema defined
            for the ProductSchema.
        user (SchemaReference[UserSchema]): Referenced to the UserSchema, indicating
            that it is a reference to another schema, specifically the UserSchema.
        event_type (String): Required to define the type of event being tracked
            or monitored, which can be used for categorization and filtering purposes.
        id (IdField): Not further defined within this code snippet, suggesting it
            might be a unique identifier for the event.
        created_at (CreatedAtField): A field representing the timestamp when the
            event was created.

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
