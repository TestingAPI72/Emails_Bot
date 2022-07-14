import pdb
import re
import smtplib
import ssl
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import strftime, gmtime

from extractdoc import get_docx_text
from list_of_files import list_of_files
import os


class run_file:

    """if we are doing unit testing, Please uncomment below lines and inherit list_of_files class (when running this
    file only) """

    def __init__(self):
        # list_of_files.__init__(self)
        # self.disk_cleanup()
        # self.download_files_from_gmail()
        self.files = ['TestingJobs_Full.docx']

    def pre_cleanup_txt(self):
        _cwd = os.getcwd()
        for _txt in os.listdir(_cwd):
            if _txt.endswith('.txt'):
                os.remove(_txt)

    def call_bot(self):
        count = 0
        if self.check_files_present():
            count += 1
        if self.change_docx_to_text():
            count += 1
        if count >= 2:
            return True

    def check_files_present(self):
        """
        Method will check whether google drive files are present are not
        :return:
        """
        if not os.path.exists(f'./Files/{self.files[0]}'):
            raise IOError("FILE NOT FOUND")
        else:
            return True

    def change_docx_to_text(self):
        """
        This method will change docx file to program readable file
        :return: Boolean
        """
        assert len(self.files) == 1, "Two files should be there"
        for _file in self.files:
            _built_path = f'./Files/{_file}'
            print(_built_path)
            emails_data = get_docx_text(_built_path)
            _file = _file.rstrip('.docx')
            print(_file)
            try:
                docx_data = open(f'{_file}' + '.txt', 'wb+')
                docx_data.write(emails_data)
                self.generator_email(file_name=_file)
                docx_data.close()
            except IOError as e:
                print(f"Problem in writing doc file into text --> {e}")
        return True

    def generator_email(self, file_name):
        """
        This will generating emails with help of regex and will store it in a file
        :param file_name:
        :return: None
        """

        try:
            docx_data = open(f'{file_name}' + '.txt', 'rb')
            generating_email_id = open('emails_id.txt', 'a+')
            output = docx_data.read().decode(encoding='utf-8', errors='ignore')
            for i in re.finditer('([(_.)A-Z|a-z|0-9]+(\.[A-Z|a-z|0-9]+)*@[a-z]+(\.[a-z]+)+)', output):
                print(i.group())
                generating_email_id.write(i.group() + '\n')
            generating_email_id.close()
            docx_data.close()
        except IOError as e:
            print(f"Problem in filtering the emails from txt file {e}")

    def get_emails(self):
        """
        This will add emails into list for further processing(SMTP)
        :return:
        """
        try:
            emails_id = open('emails_id.txt', 'r')
            emails_id_list = []
            email_address = emails_id.readline()
            while email_address != '':
                without_char = email_address.replace('\n', '')
                emails_id_list.append(without_char)
                email_address = emails_id.readline()
            emails_id.close()
            return emails_id_list
        except:
            print(sys.exc_info())

    # def sending_emails(self):
    #     """
    #     This function will send emails
    #     :param None:
    #     :return None:
    #     """
    #     try:
    #             today_date = strftime("%a, %d %b %Y ", gmtime())
    #             new_pass = self.unlocking_password(password=data_stored['User_information']['Password'])
    #             body_pattern = "Hi,\n" \
    #                            f"\n{data_stored['User_information']['User_info']}+ years of experience in Software Testing ( Manual and Automation Testing)\n" \
    #                            "\nPFA Resume \n" \
    #                            f"\nI will be available today ({today_date}) between 10:30 AM to 10:00 PM for the Google hangouts/ Zoom interviews. \n" \
    #                            "\nPlease check the panel availability and confirm the interview timings.\n" \
    #                            f"1) Overall experience:{data_stored['User_information']['User_info']} +Years\n" \
    #                            "2) Current Salary: 4.80 lakhs\n" \
    #                            "3) Expected Salary: as per company norms\n" \
    #                            "4) Max Time required to join: 2 weeks\n" \
    #                            "5) Relocation: Yes\n" \
    #                            "6) Testing certification: ISEB Certified\n" \
    #                            "7) Education : B.Tech\n" \
    #                            "\nThanks & Regards,\n" \
    #                            f"{data_stored['User_information']['User_name']}"
    #             subject = "ISEB Certified Tester---Test Engineer Openings--Manual || Automation Test Engineer || --2 Weeks notice period"
    #             body = body_pattern
    #             sender_email = ""
    #             receiver_email = self.get_emails()
    #             password = new_pass
    #             message = MIMEMultipart()
    #             message["From"] = sender_email
    #             message["Subject"] = subject
    #             message.attach(MIMEText(body, "plain"))
    #             with open(filename, "rb") as attachment:
    #                 part = MIMEBase("application", "octet-stream")
    #                 part.set_payload(attachment.read())
    #             encoders.encode_base64(part)
    #             part.add_header(
    #                 "Content-Disposition",
    #                 f"attachment; filename= {filename}",
    #             )
    #             message.attach(part)
    #             text = message.as_string()
    #             context = ssl.create_default_context()
    #             with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    #                 server.login(sender_email, password)
    #                 server.sendmail(sender_email, receiver_email, text)
    #         except smtplib.SMTPResponseException as e:
    #             print(f"Problem in email design technique {e}")
    #     except Exception as e:
    #         print(f"Problem in sending emails function {e}")
