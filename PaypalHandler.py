import requests

# PayPal API Information
PaypalClient = b"PAYPAL Client"
PaypalSecurity = b"PAYPAL SECRET KEY"
PaypalEndpoint = "https://api-m.paypal.com/"
PaypalDeleteSubEndpoint = PaypalEndpoint + "v1/billing/subscriptions/%s/cancel"


# Gets the PayPal Auth Token
def getAuthToken():
    r = requests.post(PaypalEndpoint + "v1/oauth2/token",
                      data={"grant_type": "client_credentials"},
                      auth=(PaypalClient, PaypalSecurity),
                      headers={"Authorizaion": "Basic %s:%s" % (PaypalClient, PaypalSecurity)})
    return r.json()["access_token"]


# Gets the headers we send to PayPal
def getHeaders():
    PaypalHeaders = {
        "Authorization": "Bearer %s" % getAuthToken(),
        "Content-Type": "application/json",
        'User-agent': 'WordFilter UA'
    }
    return PaypalHeaders


# Cancels a users subscription by ID
def cancelSubscription(subscriptionID):
    r = requests.post(PaypalDeleteSubEndpoint % subscriptionID, headers=getHeaders())
    return r.status_code == 204
