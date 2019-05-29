from django.core.mail import EmailMultiAlternatives
from sea.settings import DEFAULT_FROM_EMAIL


sub = "Activate your PinBooster at {shop}"
contents = """
Hi there,<br/>
<br/>
Very glad to see you here, and welcome to explore the powerful Pinterest APP of "PinBooster".<br/>
<br/>
You have already download the "PinBooster" and this email is notice to you that your shopify will be related with PinBooster System.<br/>
<br/>
The information of the register are:<br/>
<br/>
Usename: {username}<br/>
<br/>
Registration Password:  {password}<br/>
<br/>
Here you need to click the following link to activete your PinBooster account.<br/>
<br/>
Please click the following activation link:<br/>
<br/>
https://pinbooster.seamarketings.com/login?code={code}&username={username}<br/>
<br/>
After you activete the link please log in with your registration information again, then you can use the PinBooster in normal.<br/>
<br/>
Thanks,<br/>

PinBooster Customer Support
"""


class SMS(EmailMultiAlternatives):
    """发送邮件"""
    def __init__(self, content, to,):
        email_comtents = contents.format(username=content["username"], password=content["password"], code=content["code"])
        super(SMS, self).__init__(subject=sub.format(shop=content["username"]), body=email_comtents, from_email=DEFAULT_FROM_EMAIL, to=to)

    def send_email(self,):
        self.content_subtype = "html"
        self.send()


if __name__ == '__main__':
    pass