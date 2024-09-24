import frappe
from frappe import auth

@frappe.whitelist(allow_guest=True)
def login():
    frappe.logger().info(f"Form Dict: {frappe.form_dict}")
    usr = frappe.form_dict.get('usr')
    pwd = frappe.form_dict.get('pwd')

    if not usr or not pwd:
        frappe.local.response["message"] = {
            "success_key": 0,
            "message": "Missing username or password"
        }
        return

    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key": 0,
            "message": "Authentication Error!"
        }
        return

    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    frappe.response["message"] = {
        "success_key": 1,
        "message": "Authentication successful",
        "sid": frappe.session.sid,
        "api_key": user.api_key,
        "api_secret": api_generate,
        "username": user.username,
        "email": user.email,
        "gender":user.gender,
        "mobile":user.mobile_no
    }


def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    if not user_details.api_secret:
        user_details.api_secret = api_secret

    user_details.save()

    return user_details.api_secret
