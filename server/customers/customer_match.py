import uuid
from ga_runner import create_client, handleGoogleAdsException

def create_customer_match_user_list(token,customer_id):
    """Creates a Customer Match user list.

    Args:
        client: The Google Ads client.
        customer_id: The ID for the customer that owns the user list.

    Returns:
        The string resource name of the newly created user list.
    """
    #Create Google Ads Client
    client = create_client(token)
    # Creates the UserListService client.
    user_list_service_client = client.get_service("UserListService")

    # Creates the user list operation.
    user_list_operation = client.get_type("UserListOperation")

    # Creates the new user list.
    user_list = user_list_operation.create
    user_list.name = f"Customer Match list #{uuid.uuid4()}"
    user_list.description = (
        "A list of customers that originated from email and physical addresses"
    )
    # Sets the upload key type to indicate the type of identifier that is used
    # to add users to the list. This field is immutable and required for a
    # CREATE operation.
    user_list.crm_based_user_list.upload_key_type = (
        client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
    )
    # Customer Match user lists can set an unlimited membership life span;
    # to do so, use the special life span value 10000. Otherwise, membership
    # life span must be between 0 and 540 days inclusive. See:
    # https://developers.devsite.corp.google.com/google-ads/api/reference/rpc/latest/UserList#membership_life_span
    # Sets the membership life span to 30 days.
    user_list.membership_life_span = 30

    response = user_list_service_client.mutate_user_lists(
        customer_id=customer_id, operations=[user_list_operation]
    )
    user_list_resource_name = response.results[0].resource_name
    print(
        f"User list with resource name '{user_list_resource_name}' was created."
    )

    return user_list_resource_name