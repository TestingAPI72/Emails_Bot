import re
import sys
import time
import os
import requests

from Run_File import run_file
from list_of_files import list_of_files
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

"""
Updater : We need API KEY we got from BOT_FATHER in TELEGRAM
"""

updater = Updater("5514891554:AAGTaIuIYK1DBIVA2u2kzsE-mY35a2AGzSg",
                  use_context=True)

file_obj = run_file()
gmail_obj = list_of_files()

"""
Update: Will Invoke Everytime a bot receives an update(Message or command)
"""

_user_name = None


def start(update: Update, context: CallbackContext):
    gmail_obj.disk_cleanup()
    file_obj.pre_cleanup_txt()
    update.message.reply_text(
        f"Hello {_user_name}, Welcome to the Emails Bot."
        f"Please send your data in below listed format(Eg:name,email,email_password,year_of_exp,notice_period)"
        f"To Encrypt Your Password, Please Contact Admin")


def helpme(update: Update, context: CallbackContext):
    update.message.reply_text("Available Commands :-\n"
                              "	/Downloadfiles - To download files from  google drive\n"
                              "	/EmailsListOnly - To get EmailsListOnly\n"
                              "/DisplayEmails - To display emails !!!(Please type this command after Downloadfiles, "
                              "EmailsListOnly "
                              "/RunJenkins - download files and convert it and shoot out email(Please run this "
                              "command if you are not using above listed commands)")


def get_files_from_drive(update: Update, context: CallbackContext):
    update.message.reply_text("Downloading files from google drive")
    _status = gmail_obj.download_files_from_gmail()
    time.sleep(2)
    if _status:
        update.message.reply_text("Files got downloaded Successfully")
    else:
        sys.exit(-1)


def converter_files_to_emails(update: Update, context: CallbackContext):
    update.message.reply_text("Converting data in files to emails")
    _status = file_obj.call_bot()
    time.sleep(2)
    if _status:
        update.message.reply_text("Emails are generated successfully")
    else:
        sys.exit(-1)


def display_emails_via_bot(update: Update, context: CallbackContext):
    update.message.reply_text("Displaying emails")
    _emails_list = file_obj.get_emails()
    time.sleep(2)
    update.message.reply_text(_emails_list)


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)


def stop(update: Update, context: CallbackContext):
    _build_number = os.getenv('BUILD_NUMBER')
    print(_build_number)
    jenkins_uri = '192.168.0.171:8080'
    job_name = 'Telegram_Monitoring_Bot'
    stop_build_url =f'http://{jenkins_uri}/job/{job_name}/{_build_number}/stop'
    count=2
    while count!=0:
      requests.post(stop_build_url)
      count-=1


def resume_check(update: Update, context: CallbackContext):
    if file_obj.resume_exists():
        update.message.reply_text("Resume Exists")
    else:
        update.message.reply_text("Resume Not Exists in our Database, Please check with admin")


def welcome(user_input=None):
    global _user_name
    _user_name = user_input
    answer = f'Hi {_user_name}, Please Upload Your Resume in docx format and ' \
             f'Type /Stop and Wait for few seconds..... and' \
             f' type /start command to restart the bot and enter your name again'
    return answer


def data_collector(data=None):
    if data.find(','):
        return data.split()


def build_jenkins(update: Update, context: CallbackContext):
    user_data = data_collector()
    assert len(user_data) > 2, "INSUFFICIENT DATA PROVIDED"
    QUEUE_POLL_INTERVAL = 2
    JOB_POLL_INTERVAL = 20
    OVERALL_TIMEOUT = 14400  # 4 hour
    auth_token = '1174840704eb978d8e807d50ff06a53653'
    jenkins_uri = '192.168.0.171:8080'
    job_name = 'Send_Emails'
    # start the build

    start_build_url = f'http://{jenkins_uri}/job/{job_name}/buildWithParameters?token={auth_token}&Name={user_data[0]}' \
                      f'&Email={user_data[1]}&Password={user_data[2]}&Years_Of_Experience={user_data[3]}&Notice_Period={user_data[4]}'
    response = requests.post(start_build_url)

    # from return headers get job queue location
    #
    m = re.match(r"http.+(queue.+)\/", response.headers['Location'])
    if not m:
        # To Do: handle error
        print("Job started request did not have queue location")
        sys.exit(1)

    # poll the queue looking for job to start
    #
    queue_id = m.group(1)
    job_info_url = 'http://{}/{}/api/json'.format(jenkins_uri, queue_id)
    elasped_time = 0
    print('{} Job {} added to queue: {}'.format(time.ctime(), job_name, job_info_url))
    while True:
        l = requests.get(job_info_url)
        jqe = l.json()
        task = jqe['task']['name']
        try:
            job_id = jqe['executable']['number']
            break
        except:
            time.sleep(QUEUE_POLL_INTERVAL)
            elasped_time += QUEUE_POLL_INTERVAL

        if (elasped_time % (QUEUE_POLL_INTERVAL * 10)) == 0:
            print("{}: Job {} not started yet from {}".format(time.ctime(), job_name, queue_id))

    # poll job status waiting for a result
    #
    job_url = 'http://{}/job/{}/{}/api/json'.format(jenkins_uri, job_name, job_id)
    start_epoch = int(time.time())
    while True:
        print("{}: Job started URL: {}".format(time.ctime(), job_url))
        j = requests.get(job_url)
        jje = j.json()
        result = jje['result']
        if result == 'SUCCESS':
            # Do success steps
            print("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            break
        elif result == 'FAILURE':
            # Do failure steps
            print("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            break
        elif result == 'ABORTED':
            # Do aborted steps
            print("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            break
        else:
            print("{}: Job: {} Status: {}. Polling again in {} secs".format(
                time.ctime(), job_name, result, JOB_POLL_INTERVAL))

        cur_epoch = int(time.time())
        if (cur_epoch - start_epoch) > OVERALL_TIMEOUT:
            print("No status before timeout of {} secs".format(OVERALL_TIMEOUT))
            sys.exit(1)

        time.sleep(JOB_POLL_INTERVAL)


def downloader(update: Update, context: CallbackContext):
    context.bot.get_file(update.message.document).download()

    with open("Resume.docx", 'wb') as f:
        context.bot.get_file(update.message.document).download(out=f)


def reply(update, context: CallbackContext):
    user_input = update.message.text
    update.message.reply_text(welcome(user_input))
    data_collector(user_input)


"""
CommandHandler : Is Used to Handle any command sent by user(EG:/help)
"""

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', helpme))
updater.dispatcher.add_handler(CommandHandler('Downloadfiles', get_files_from_drive))
updater.dispatcher.add_handler(CommandHandler('Emailslistonly', converter_files_to_emails))
updater.dispatcher.add_handler(CommandHandler('Displayemails', display_emails_via_bot))
updater.dispatcher.add_handler(CommandHandler('Stop', stop))
updater.dispatcher.add_handler(CommandHandler('RunJenkins', build_jenkins))
updater.dispatcher.add_handler(CommandHandler('Resume', resume_check))
updater.dispatcher.add_handler(MessageHandler(Filters.document, downloader))
updater.dispatcher.add_handler(MessageHandler(Filters.text, reply))
updater.dispatcher.add_handler(MessageHandler(
    Filters.command, unknown))  # Filters out unknown commands

"""
MessageHandler: Is Used to Handle Normal Message sent by user(Eg:Stop)
"""

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.start_polling()
