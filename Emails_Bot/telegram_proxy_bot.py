import sys
import time
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

updater = Updater("5514891554:AAHORfrYjWxVaWdu4gd8HKMKSGsROwdJBTw",
                  use_context=True)

file_obj = run_file()
gmail_obj = list_of_files()

"""
Update: Will Invoke Everytime a bot receives an update(Message or command)
"""


def start(update: Update, context: CallbackContext):
    gmail_obj.disk_cleanup()
    file_obj.pre_cleanup_txt()
    update.message.reply_text(
        "Hello sir, Welcome to the Bot.Please write /help command to see lists of available commands")


def helpme(update: Update, context: CallbackContext):
    update.message.reply_text("Available Commands :-\n"
                              "	/Downloadfiles - To download files from  google drive\n"
                              "	/EmailsListOnly - To get EmailsListOnly\n"
                              "/DisplayEmails - To display emails !!!(Please type this command after Downloadfiles, "
                              "EmailsListOnly "
                              " /Build - download files and convert it and shoot out email")


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


def build_project(update: Update, context: CallbackContext):
    update.message.reply_text("Building Jenkins Project, Wait for few minutes")


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)


def stop(update: Update, context: CallbackContext):
    update.message.reply_text("Stopping the process")
    sys.exit(0)


"""
CommandHandler : Is Used to Handle any command sent by user(EG:/help)
"""

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', helpme))
updater.dispatcher.add_handler(CommandHandler('Downloadfiles', get_files_from_drive))
updater.dispatcher.add_handler(CommandHandler('emailslistonly', converter_files_to_emails))
updater.dispatcher.add_handler(CommandHandler('displayemails', display_emails_via_bot))
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(
    Filters.command, unknown))  # Filters out unknown commands

"""
MessageHandler: Is Used to Handle Normal Message sent by user(Eg:Stop)
"""

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.start_polling()
