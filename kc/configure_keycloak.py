"""
This python script is used to initialize and configure keycloak.
"""

import os
import sys

from keycloak import KeycloakAdmin, KeycloakAuthenticationError, KeycloakPostError

# ----------------------------------------- #
#               ENVIRONMENT                 #
# ----------------------------------------- #

KC_BOOTSTRAP_ADMIN_USERNAME = os.getenv("KC_BOOTSTRAP_ADMIN_USERNAME")
KC_BOOTSTRAP_ADMIN_PASSWORD = os.getenv("KC_BOOTSTRAP_ADMIN_PASSWORD")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")

KC_ADMIN_USERNAME = os.getenv("KC_ADMIN_USERNAME")
KC_ADMIN_PASSWORD = os.getenv("KC_ADMIN_PASSWORD")
KC_ADMIN_EMAIL = os.getenv("KC_ADMIN_EMAIL")

KEYCLOAK_BACKEND_CLIENT_ID = os.getenv("KEYCLOAK_BACKEND_CLIENT_ID")
KEYCLOAK_FRONTEND_CLIENT_ID = os.getenv("KEYCLOAK_FRONTEND_CLIENT_ID")

KEYCLOAK_REALM_ROLES = os.getenv("KEYCLOAK_REALM_ROLES")
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
FRONTEND_EXT_URL = os.getenv("FRONTEND_EXT_URL")
BACKEND_EXT_URL = os.getenv("BACKEND_EXT_URL")

KEYCLOAK_REDIRECT_URI = os.getenv("KEYCLOAK_REDIRECT_URI")
POST_LOGOUT_REDIRECT_URI = os.getenv("POST_LOGOUT_REDIRECT_URI")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
DISPLAY_NAME = os.getenv("DISPLAY_NAME")


def initialize_keycloak_admin(username: str, password: str) -> KeycloakAdmin:
    """
    Initialize the Keycloak Admin client.
    """
    try:
        kc = KeycloakAdmin(
            server_url=KEYCLOAK_URL,
            username=username,
            password=password,
            realm_name=KEYCLOAK_REALM,
            verify=True,
        )

        # Verify connection by fetching the realm
        kc.get_realm(KEYCLOAK_REALM)
        return kc
    except KeycloakAuthenticationError:
        print("Failed to initialize Bootstrap Keycloak Admin...")
        sys.exit(0)


def enable_service_account(keycloak_admin: KeycloakAdmin, client_id: str):
    """
    Enable service account for a given client and assign the admin role.
    This only applies to private clients, such that they are able to
    perform admin tasks programmatically. (e.g. MinIO, WiseFood-API etc.)
    """
    try:
        # Retrieve the client configuration
        client_representation = keycloak_admin.get_client(client_id)

        # Update the configuration to enable service accounts
        client_representation["serviceAccountsEnabled"] = True
        client_representation["authorizationServicesEnabled"] = True

        # Update the client with the modified configuration
        keycloak_admin.update_client(client_id, client_representation)
        print(f"Service account enabled for client with ID: {client_id}")
        role = keycloak_admin.get_realm_role("admin")
        print(f"Retrieved existing role: {role}")
        service_account_user = keycloak_admin.get_client_service_account_user(client_id)
        service_account_user_id = service_account_user["id"]

        # Assign the admin role to the service account user
        keycloak_admin.assign_realm_roles(service_account_user_id, [role])
        print(f"Admin role assigned to service account for client ID: {client_id}")
    except KeycloakPostError as e:
        print(f"Failed to enable service account: {e}")
        raise


if __name__ == "__main__":

    try:
        kc_admin = initialize_keycloak_admin(
            username=KC_BOOTSTRAP_ADMIN_USERNAME, password=KC_BOOTSTRAP_ADMIN_PASSWORD
        )
    except KeycloakPostError:
        print("Bootstrap admin does not exist. Keycloak already configured. Exiting...")
        sys.exit(0)

    backend_client_representation = {
        "clientId": KEYCLOAK_BACKEND_CLIENT_ID,
        "enabled": True,
        "publicClient": False,
        "rootUrl": "",
        "baseUrl": "",
        "redirectUris": ["*"],
        "attributes": {"post.logout.redirect.uris": "+"},
        "directAccessGrantsEnabled": True,
    }

    backend_client_id = kc_admin.create_client(
        backend_client_representation, skip_exists=True
    )

    enable_service_account(keycloak_admin=kc_admin, client_id=backend_client_id)

    client = kc_admin.get_client(backend_client_id)
    client["name"] = "Openfincal API"
    client["description"] = "Backend API client for Openfincal"
    kc_admin.update_client(backend_client_id, client)

    # Save client Secret.
    client_secret = kc_admin.get_client_secrets(backend_client_id)["value"]

    with open("/usr/shared/client-secret.txt", "w", encoding="utf-8") as file:
        file.write(client_secret)
        file.close()

    # Configure Frontend Client
    frontend_client_representation = {
        "clientId": KEYCLOAK_FRONTEND_CLIENT_ID,
        "enabled": True,
        "publicClient": True,
        "name": "Openfincal UI",
        "description": "Frontend public client for Openfincal",
        "rootUrl": FRONTEND_EXT_URL,
        "baseUrl": FRONTEND_EXT_URL,
        "redirectUris": [
            KEYCLOAK_REDIRECT_URI,
        ],
        "attributes": {"post.logout.redirect.uris": POST_LOGOUT_REDIRECT_URI},
        "directAccessGrantsEnabled": True,
    }
    frontend_client_id = kc_admin.create_client(
        frontend_client_representation, skip_exists=True
    )

    # Create new Admin user
    admin_id = kc_admin.create_user(
        {
            "username": KC_ADMIN_USERNAME,
            "firstName": "Openfincal",
            "lastName": "Administrator",
            "email": KC_ADMIN_EMAIL,
            "enabled": True,
            "emailVerified": True,
            "credentials": [
                {"value": KC_ADMIN_PASSWORD, "type": "password", "temporary": False}
            ],
        },
        exist_ok=True,
    )

    kc_admin.assign_realm_roles(admin_id, [kc_admin.get_realm_role("admin")])

    # Change Realm representation Settings.
    realm = kc_admin.get_realm(KEYCLOAK_REALM)
    realm["accessTokenLifespan"] = 60
    realm["rememberMe"] = True
    realm["verifyEmail"] = True
    realm["resetPasswordAllowed"] = True
    realm["supportedLocales"] = [
        "de",
        "nl",
        "no",
        "fi",
        "pt",
        "el",
        "lt",
        "en",
        "lv",
        "it",
        "fr",
        "hu",
        "es",
        "cs",
        "uk",
        "sk",
        "pl",
        "da",
    ]

    realm["registrationAllowed"] = True
    realm["editUsernameAllowed"] = True
    realm["registrationEmailAsUsername"] = False
    realm["bruteForceProtected"] = True

    # Add Google IDP
    google_idp = {
        "alias": "google",
        "providerId": "google",
        "enabled": True,
        "updateProfileFirstLoginMode": "on",
        "trustEmail": True,
        "storeToken": True,
        "addReadTokenRoleOnCreate": False,
        "authenticateByDefault": False,
        "linkOnly": False,
        "config": {
            "hideOnLoginPage": "false",
            "acceptsPromptNoneForwardFromClient": "false",
            "clientId": GOOGLE_CLIENT_ID,
            "disableUserInfo": "false",
            "filteredByClaim": "false",
            "syncMode": "LEGACY",
            "userIp": "false",
            "clientSecret": GOOGLE_CLIENT_SECRET,
            "caseSensitiveOriginalUsername": "false",
            "guiOrder": "1",
        },
    }

    idps = realm.get("identityProviders", [])

    replaced = False
    for idx, ip in enumerate(idps):
        if ip.get("alias") == "google":
            replaced = True
            break

    if replaced:
        kc_admin.update_idp("google", google_idp)
    else:
        kc_admin.create_idp(google_idp)

    # Configure SMTP
    if SMTP_HOST and SMTP_USER and SMTP_PORT and SMTP_PASSWORD:
        realm["smtpServer"] = {
            "host": SMTP_HOST,
            "port": SMTP_PORT,
            "auth": True,
            "user": SMTP_USER,
            "password": SMTP_PASSWORD,
            "starttls": True,
            "from": SMTP_USER,
            "fromDisplayName": DISPLAY_NAME,
        }

    kc_admin.update_realm(KEYCLOAK_REALM, realm)

    kc_admin = initialize_keycloak_admin(
        username=KC_ADMIN_USERNAME, password=KC_ADMIN_PASSWORD
    )

    # Delete the original temporary admin
    kc_admin.delete_user(kc_admin.get_user_id(KC_BOOTSTRAP_ADMIN_USERNAME))

    sys.exit(0)
