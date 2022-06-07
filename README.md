# Integration of Microsoft Identity Platform and Microsoft Graph in Python

## About this sample

This repo is derived from the following sources:

1. https://github.com/Azure-Samples/ms-identity-python-webapp (mainly)
1. https://github.com/Azure-Samples/ms-identity-python-flask-webapp-authentication

### Overview

This sample demonstrates a Python web application that signs-in users with the Microsoft identity platform and calls the Microsoft Graph.

1. The python web application uses the Microsoft Authentication Library (MSAL) to obtain a JWT access token from the Microsoft identity platform (formerly Azure AD v2.0):
2. The access token is used as a bearer token to authenticate the user when calling the Microsoft Graph.

![Overview](./ReadmeFiles/topology.png)

## How to run this sample

Prerequisites:

- [Python 3.8+](https://www.python.org/downloads/)
- An Azure Active Directory (Azure AD) tenant. For more information on how to get an Azure AD tenant, see [how to get an Azure AD tenant.](https://docs.microsoft.com/azure/active-directory/develop/quickstart-create-new-tenant)


### Step 1: Clone or download this repository

From your shell or command line:

```Shell
git clone https://github.com/george-kuanli-peng/ms-identity-graph-python-webapp.git
```

or download and extract the repository .zip file.


### Step 2: Register the sample application with your Azure Active Directory tenant

> NOTE: https://github.com/Azure-Samples/ms-identity-python-webapp has PowerShell scripts
  for auto configuring an Azure Active Directory tenant

#### Choose the Azure AD tenant where you want to create your applications

As a first step you'll need to:

1. Sign in to the [Azure portal](https://portal.azure.com) using either a work or school account or a personal Microsoft account.
1. If your account is present in more than one Azure AD tenant, select your profile at the top right corner in the menu on top of the page, and then **switch directory**.
   Change your portal session to the desired Azure AD tenant.

#### Register the Python Webapp (python-webapp)

1. Navigate to the Microsoft identity platform for developers [App registrations](https://go.microsoft.com/fwlink/?linkid=2083908) page.
1. Select **New registration**.
1. When the **Register an application page** appears, enter your application's registration information:
   - In the **Name** section, enter a meaningful application name that will be displayed to users of the app, for example `python-webapp`.
   - Change **Supported account types** to **Accounts in any organizational directory and personal Microsoft accounts (e.g. Skype, Xbox, Outlook.com)**.
   - In the Redirect URI (optional) section, select **Web** in the combo-box and enter the following redirect URIs: `http://localhost:5000/getAToken`. Replace the hostname or port number when necessary.
1. Select **Register** to create the application.
1. On the app **Overview** page, find the **Application (client) ID** value and record it for later. You'll need it to configure the Visual Studio configuration file for this project.
1. Select **Save**.
1. From the **Certificates & secrets** page, in the **Client secrets** section, choose **New client secret**:

   - Type a key description (of instance `app secret`),
   - Select a key duration of either **In 1 year**, **In 2 years**, or **Never Expires**.
   - When you press the **Add** button, the key value will be displayed, copy, and save the value in a safe location.
   - You'll need this key later to configure the project in Visual Studio. This key value will not be displayed again, nor retrievable by any other means,
     so record it as soon as it is visible from the Azure portal.
   
   > TODO: app authentication with certificates
1. Select the **API permissions** section
   - Click the **Add a permission** button and then,
   - Ensure that the **Microsoft APIs** tab is selected
   - In the *Commonly used Microsoft APIs* section, click on **Microsoft Graph**
   - In the **Delegated permissions** section, ensure the following permissions are checked.
     Use the search box if necessary.

     - *User.Read*
     - *Files.Read.All*

     > NOTE: refer to subtopics of [Microsoft Graph REST APIs](https://docs.microsoft.com/en-us/onedrive/developer/rest-api) for the exact permission (scope) requirements for accessing a certain type of OneDrive's resource.
   - Select the **Add permissions** button

### Step 3: Configure the sample to use your Azure AD tenant

In the steps below, "ClientID" is the same as "Application ID" or "AppId".

#### Configure the python-webapp project

1. Make a copy of the `app_config_template.py` file and name it `app_config.py`.
1. Open the `app_config.py` file.
1. Find the app key `Enter_the_Tenant_Name_Here` and replace the existing value with your Azure AD tenant name. Uncomment this line of code and comment the previous line that defines `AUTHORITY` for multi-tenant app.
   > NOTE: Skip this step if you want to support multi-tenants or Microsoft personal accounts.
1. You saved your application secret during the creation of the `python-webapp` app in the Azure portal.
   Now you can set the secret in environment variable `CLIENT_SECRET`,
   and then adjust `app_config.py` to pick it up.
   > TODO: app authentication with certificates
1. Find the app key `Enter_the_Application_Id_here` and replace the existing value with the application ID (clientId) of the `python-webapp` application copied from the Azure portal.


### Step 4: Run the sample

- You will need to install dependencies using pip as follows:
```Shell
$ pip install -r requirements.txt
```

Run app.py from shell or command line. Note that the host and port values need to match what you've set up in your redirect_uri:

```Shell
$ flask run --host localhost --port 5000
```

## More information

For more information, see MSAL.Python's [conceptual documentation]("https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki"):


For more information about web apps scenarios on the Microsoft identity platform see [Scenario: Web app that calls web APIs](https://docs.microsoft.com/en-us/azure/active-directory/develop/scenario-web-app-call-api-overview)

For more information about how OAuth 2.0 protocols work in this scenario and other scenarios, see [Authentication Scenarios for Azure AD](http://go.microsoft.com/fwlink/?LinkId=394414).
