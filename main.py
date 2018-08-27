#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
import telegram.ext
import telegram
import datetime
import os
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

PATH = os.path.dirname(os.path.realpath(__file__)) + '/'



# loading config files
CONFIG = json.loads(open(PATH + 'conf/config.json', 'r', encoding='utf-8').read())
LANG   = json.loads(open(PATH + 'lang/' + CONFIG['Lang'] + '.json', 'r', encoding='utf-8').read())


# check config
if CONFIG['Admin'] == 0 :
	print(LANG['error_config_noadmin'])
	os._exit(0)
if CONFIG['Token'] == "0" :
	print(LANG['error_config_notoken'])
	os._exit(0)


# messege lock
MESSAGE_LOCK = False
message_list = json.loads(open(PATH + 'data/data.json', 'r', encoding='utf-8').read())
# def save_data
def save_data():
	global MESSAGE_LOCK
	while MESSAGE_LOCK:
		time.sleep(0.1)
	MESSAGE_LOCK = True
	with open(PATH + 'data/data.json', 'w', encoding='utf-8') as f:
		f.write(json.dumps(message_list))
	MESSAGE_LOCK = False


# preference lock
PREFERENCE_LOCK = False
preference_list = json.loads(open(PATH + 'data/preference.json', 'r', encoding='utf-8').read())
# def save_preference
def save_preference():
	global PREFERENCE_LOCK
	while PREFERENCE_LOCK:
		time.sleep(0.1)
	PREFERENCE_LOCK = True
	with open(PATH + 'data/preference.json', 'w', encoding='utf-8') as f:
		f.write(json.dumps(preference_list))
	PREFERENCE_LOCK = False


# def user preference init
def init_user(idf_fromuser):
	global preference_list
	if not preference_list.__contains__(str(idf_fromuser)):
		preference_list[str(idf_fromuser)] = {}

		# /say and /done
		preference_list[str(idf_fromuser)]['conversation'] = False
		# /block and /unblock
		preference_list[str(idf_fromuser)]['blacklist'] = False
		# /receipt
		preference_list[str(idf_fromuser)]['receipt'] = True
		# /markdown
		if idf_fromuser == CONFIG['Admin'] :
			preference_list[str(CONFIG['Admin'])]['markdown'] = True

		preference_list[str(idf_fromuser)]['name'] = user.full_name
		threading.Thread(target=save_preference).start()
		return
	if preference_list[str(idf_fromuser)]['name'] != user.full_name:
		preference_list[str(idf_fromuser)]['name'] = user.full_name
		threading.Thread(target=save_preference).start()


# def messege handled
def process_msg(bot, update):
	global message_list
	if update.message.from_user.id == CONFIG['Admin']:
		init_user(CONFIG['Admin'])
		if update.message.reply_to_message:
			if message_list.__contains__(str(update.message.reply_to_message.message_id)):
				tryf_update_msg = update.message
				sender_id = message_list[str(tryf_update_msg.reply_to_message.message_id)]['sender_id']
				try:
					if tryf_update_msg.audio:
						bot.send_audio(chat_id=sender_id, audio=tryf_update_msg.audio, caption=tryf_update_msg.caption)
					elif tryf_update_msg.document:
						bot.send_document(chat_id=sender_id, document=tryf_update_msg.document, caption=tryf_update_msg.caption)
					elif tryf_update_msg.voice:
						bot.send_voice(chat_id=sender_id, voice=tryf_update_msg.voice, caption=tryf_update_msg.caption)
					elif tryf_update_msg.video:
						bot.send_video(chat_id=sender_id, video=tryf_update_msg.video, caption=tryf_update_msg.caption)
					elif tryf_update_msg.sticker:
						bot.send_sticker(chat_id=sender_id, sticker=tryf_update_msg.sticker)
					elif tryf_update_msg.photo:
						bot.send_photo(chat_id=sender_id, photo=tryf_update_msg.photo[0], caption=tryf_update_msg.caption)
					elif tryf_update_msg.text_markdown:
						if preference_list[str(CONFIG['Admin'])]['markdown'] :
							bot.send_message(chat_id=sender_id, text=tryf_update_msg.text_markdown)
						else:
							bot.send_message(chat_id=sender_id, text=tryf_update_msg.text)
					else:
						bot.send_message(chat_id=CONFIG['Admin'], text=LANG['error_reply_notsupporttype'])
						return
				except Exception as e:
					if e.message == "Forbidden: bot was blocked by the user":
						bot.send_message(chat_id=CONFIG['Admin'], text=LANG['error_receipt_blockedbyuser'])
					else:
						bot.send_message(chat_id=CONFIG['Admin'], text=LANG['error_receipt_unknown'])
					return
				if preference_list[str(CONFIG['Admin'])]['receipt']:
					bot.send_message(chat_id=CONFIG['Admin'], text=LANG['receipt_admin_sent'] % (preference_list[str(sender_id)]['name'], str(sender_id)), parse_mode=telegram.ParseMode.MARKDOWN, reply_to_message_id=tryf_update_msg.message_id)
			else:
				bot.send_message(chat_id=CONFIG['Admin'], text=LANG['error_reply_nodata'])
		else:
			bot.send_message(chat_id=CONFIG['Admin'], text=LANG['error_reply_notarget'])
	else:
		idf_fromuser = update.message.from_user.id
		init_user(idf_fromuser)
		# only when 'conversation' is true
		if preference_list[str(idf_fromuser)]['conversation'] and not preference_list[str(idf_fromuser)]['blacklist'] :
			# forward messege to me
			msg_forward_to_me = bot.forward_message(chat_id=CONFIG['Admin'], from_chat_id=idf_fromuser, message_id=update.message.message_id)
			# add user-info output to me when content is sticker or photo.
			if msg_forward_to_me.sticker :
				bot.send_message(chat_id=CONFIG['Admin'], text=LANG['receipt_admin_receive'] % (update.message.from_user.full_name, str(idf_fromuser)), parse_mode=telegram.ParseMode.MARKDOWN, reply_to_message_id=msg_forward_to_me.message_id)
			# receipt to the sender
			if preference_list[str(idf_fromuser)]['receipt']:
				bot.send_message(chat_id=idf_fromuser, text=LANG['receipt_user_sent'], reply_to_message_id=update.message.message_id)
			message_list[str(msg_forward_to_me.message_id)] = {}
			message_list[str(msg_forward_to_me.message_id)]['sender_id'] = idf_fromuser
			# save_data
			threading.Thread(target=save_data).start()
		# when conversation is false
		else:
			# the sender should run /say
			bot.send_message(chat_id=idf_fromuser, text=LANG['warning_conversation_start'])
	pass


# def bot command
def process_command(bot, update):
	# load global 'CONFIG'
	global CONFIG
	# load global 'preference_list'
	global preference_list
	# define 'bot command'
	command = update.message.text[1:].replace(CONFIG['Username'], '').lower().split()[0]
	# define 'from_user.id'
	idf_fromuser = update.message.from_user.id
	# init user
	init_user(idf_fromuser)
	## remove 'chat.id' due to the work by 'handlerf_Filters.private'
	##define 'chat.id'
	#idf_chat = update.message.chat_id
	##while equvalent to update.message.from_user.id

	if not preference_list[str(idf_fromuser)]['blacklist'] or idf_fromuser == CONFIG['Admin'] :
		# bot directives independent to 'conversation' :
		##bot start
		if command == 'start' :
			bot.send_message(chat_id=idf_fromuser, text=LANG['info_start'])
			return
		##start conversation
		elif command == 'say' :
			preference_list[str(idf_fromuser)]['conversation'] = True
			threading.Thread(target=save_preference).start()
			bot.send_message(chat_id=idf_fromuser, text=LANG['notify_conversation_start'])
		##end conversation
		elif command == 'done' :
			preference_list[str(idf_fromuser)]['conversation'] = False
			threading.Thread(target=save_preference).start()
			bot.send_message(chat_id=idf_fromuser, text=LANG['notify_conversation_end'])
		##messege-info you point
		elif command == 'msginfo' :
			if (idf_fromuser == CONFIG['Admin']) :
				if update.message.reply_to_message:
					if message_list.__contains__(str(update.message.reply_to_message.message_id)):
						idf_replytomessege_messegeid = update.message.reply_to_message.message_id
						sender_id = message_list[str(idf_replytomessege_messegeid)]['sender_id']
						bot.send_message(chat_id=idf_fromuser, text=LANG['receipt_admin_receive'] % (preference_list[str(sender_id)]['name'], str(sender_id)), parse_mode=telegram.ParseMode.MARKDOWN, reply_to_message_id=idf_replytomessege_messegeid)
					else:
						bot.send_message(chat_id=idf_fromuser, text=LANG['error_reply_nodata'])
			else:
				bot.send_message(chat_id=idf_fromuser, text=LANG['warning_user_adminonly'])
		##blacklist function to block user
		elif command == 'block' :
			if (idf_fromuser == CONFIG['Admin']) :
				if update.message.reply_to_message:
					if message_list.__contains__(str(update.message.reply_to_message.message_id)):
						preference_list[str(idf_fromuser)]['blacklist'] = True
						threading.Thread(target=save_preference).start()
						bot.send_message(chat_id=idf_fromuser, text=LANG['operation_block'])
					else:
						bot.send_message(chat_id=idf_fromuser, text=LANG['error_reply_nodata'])
			else:
				bot.send_message(chat_id=idf_fromuser, text=LANG['warning_user_adminonly'])
		##blacklist function to unblock user
		elif command == 'unblock' :
			if (idf_fromuser == CONFIG['Admin']) :
				if update.message.reply_to_message:
					if message_list.__contains__(str(update.message.reply_to_message.message_id)):
						preference_list[str(idf_fromuser)]['blacklist'] = False
						threading.Thread(target=save_preference).start()
						bot.send_message(chat_id=idf_fromuser, text=LANG['operation_unblock'])
					else:
						bot.send_message(chat_id=idf_fromuser, text=LANG['error_reply_nodata'])
			else:
				bot.send_message(chat_id=idf_fromuser, text=LANG['warning_user_adminonly'])
		##switch markdown
		elif command == 'markdown' :
			preference_list[str(CONFIG['Admin'])]['markdown'] = (preference_list[str(CONFIG['Admin'])]['markdown'] == False)
			threading.Thread(target=save_preference).start()
			if preference_list[str(CONFIG['Admin'])]['markdown'] :
				bot.send_message(chat_id=CONFIG['Admin'], text=LANG['operation_markdown_enable'])
			else:
				bot.send_message(chat_id=CONFIG['Admin'], text=LANG['operation_markdown_disable'])
		# only when 'conversation' false, can operate other bot directives, as to make /done useful
		elif not preference_list[str(idf_fromuser)]['conversation'] :
			##switch receipt
			if command == 'receipt' :
				preference_list[str(idf_fromuser)]['receipt'] = (preference_list[str(idf_fromuser)]['receipt'] == False)
				threading.Thread(target=save_preference).start()
				if preference_list[str(idf_fromuser)]['receipt']:
					bot.send_message(chat_id=idf_fromuser, text=LANG['info_receipt_on'])
				else:
					bot.send_message(chat_id=idf_fromuser, text=LANG['info_receipt_off'])
			##bot version
			elif command == 'version' :
				bot.send_message(chat_id=idf_fromuser, text=LANG['info_version'])
			else:
				##when received not existed command
				bot.send_message(chat_id=idf_fromuser, text=LANG['warning_user_commandnotfound'])
		# ask user to /done
		else:
			bot.send_message(chat_id=idf_fromuser, text=LANG['warning_conversation_end'])
	else:
		#cancel /block notification to user output.
		#bot.send_message(chat_id=idf_fromuser, text=LANG['warning_user_blocked'])
		return



# define name 'updaterf'
updaterf = telegram.ext.Updater(token=CONFIG['Token'])

# handler defined
handlerf_addhandler = updaterf.dispatcher.add_handler
handlerf_MessageHandler = telegram.ext.MessageHandler
handlerf_Filters = telegram.ext.Filters
# receive command
handlerf_addhandler(handlerf_MessageHandler(handlerf_Filters.command & handlerf_Filters.private, process_command))
# receive messege
handlerf_addhandler(handlerf_MessageHandler(handlerf_Filters.all & handlerf_Filters.private & (~ handlerf_Filters.command) & (~ handlerf_Filters.status_update), process_msg))

# generate user-info
mef = updaterf.bot.get_me()
CONFIG['ID'] = mef.id
CONFIG['Username'] = '@' + mef.username
# print user-info in server
print("Starting... (ID: {0}, Username: {1})".format(CONFIG['ID'], CONFIG['Username']))

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot
# To start the bot, run
##polling query for the tg center periodically
updaterf.start_polling()
print("Started")

# you probably want to stop the Bot by pressing Ctrl+C or sending a signal to the Bot process
updaterf.idle()
print("Stopping...")
save_data()
save_preference()
print("Data Saved.")
print("Stopped.")
