from cProfile import run
import pstats
from pyobigram.utils import sizeof_fmt,get_file_size,createID,nice_time
from pyobigram.client import ObigramClient,inlineQueryResultArticle
from MoodleClient import MoodleClient

from JDatabase import JsonDatabase
import zipfile
import os
import infos
import xdlink
import mediafire
import datetime
import time
import requests
from bs4 import BeautifulSoup
from pydownloader.downloader import Downloader
from ProxyCloud import ProxyCloud
import ProxyCloud
import socket
import tlmedia
import S5Crypto
import asyncio
import aiohttp
import moodlews
import moodle_client
from moodle_client import MoodleClient2
from yarl import URL
import re
import random
from draft_to_calendar import send_calendar
import uptodown

def sign_url(token: str, url: URL):
    query: dict = dict(url.query)
    query["token"] = token
    path = "webservice" + url.path
    return url.with_path(path).with_query(query)

def short_url(url):
    api = 'https://shortest.link/es/'
    resp = requests.post(api,data={'url':url})
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text,'html.parser')
        shorten = soup.find('input',{'class':'short-url'})['value']
        return shorten
    return url

def downloadFile(downloader,filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        thread = args[2]
        if thread.getStore('stop'):
            downloader.stop()
        downloadingInfo = infos.createDownloading(filename,totalBits,currentBits,speed,time,tid=thread.id)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def uploadFile(filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        originalfile = args[2]
        thread = args[3]
        downloadingInfo = infos.createUploading(filename,totalBits,currentBits,speed,time,originalfile)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def processUploadFiles(filename,filesize,files,update,bot,message,thread=None,jdb=None):
    try:
        err = None
        bot.editMessageText(message,'Iniciando Sesión')
        fileid = None
        user_info = jdb.get_user(update.message.sender.username)
        cloudtype = user_info['cloudtype']
        proxy = ProxyCloud.parse(user_info['proxy'])
        draftlist=[]
        if cloudtype == 'moodle':
            host = user_info['moodle_host']
            token = user_info['token']
            print(token)
            for file in files:
                    data = asyncio.run(moodlews.webservice_upload_file(host,token,file,progressfunc=uploadFile,proxy=proxy,args=(bot,message,filename,thread)))
                    while not moodlews.store_exist(file):pass
                    data = moodlews.get_store(file)
                    if data[0]:
                        urls = moodlews.make_draft_urls(data[0])
                        draftlist.append({'file':file,'url':urls[0]})
                        file_size = None
                        host = urls[0].split('/draftfile')[0]+'/'
                        linkdraft = urls[0].split(host)[1]
                        token = '?token='+token
                        urls = host+'webservice/'+linkdraft+token
                        urls = short_url(urls)
                        finishInfo = infos.createFinishUploading(file,file_size,urls,update.message.sender.username)
                        bot.sendMessage(message.chat.id,finishInfo,parse_mode='html')
                    else:
                        err = data[1]
                        print(err)
                        bot.editMessageText(message,'Error\n' + str(err))
        return draftlist,err
    except Exception as ex:
        bot.editMessageText(message,'Error:\n1-Compruebe que la nube esta activa\n2-Verifique su proxy\n3-O revise su cuenta')

id = ''
def processFile(update,bot,message,file,thread=None,jdb=None):
    global id
    file_size = get_file_size(file)
    getUser = jdb.get_user(update.message.sender.username)
    max_file_size = 1024 * 1024 * getUser['zips']
    file_upload_count = 0
    findex = 0
    id = createID()
    os.rename(file, 'name'+id+'.dm')
    file = 'name'+id+'.dm'
    if file_size > max_file_size:
        compresingInfo = infos.createCompresing(file,file_size,max_file_size)
        bot.editMessageText(message,compresingInfo)
        zipname = str(file).split('.')[0] + createID()
        mult_file = zipfile.MultiFile(zipname,max_file_size)
        zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(file)
        zip.close()
        mult_file.close()
        data,err = processUploadFiles(file,file_size,mult_file.files,update,bot,message,jdb=jdb)
        try:
            os.unlink(file)
        except:pass
        file_upload_count = len(zipfile.files)
    else:
        data,err = processUploadFiles(file,file_size,[file],update,bot,message,jdb=jdb)
        file_upload_count = 1
    bot.editMessageText(message,'📝Creando TxT📝')
    bot.deleteMessage(message.chat.id,message.message_id)
    files = []
    if data:
        for draft in data:
            files.append({'name':draft['file'],'directurl':draft['url']})
    i=0
    while i < len(files):
        if i+1 < len(files):
            print('Más de 1 Links ')
        i+=2
    if len(files) > 0:     
        txtname = str(file).split('/')[-1].split('.')[0] + '.txt'
        txtname = txtname.replace(' ','')
        sendTxt(txtname,files,update,bot)
   
def ddl(update,bot,message,url,file_name='',thread=None,jdb=None):
    downloader = Downloader()
    file = downloader.download_url(url,progressfunc=downloadFile,args=(bot,message,thread))
    if not downloader.stoping:
        if file:
            processFile(update,bot,message,file,jdb=jdb)

def sendTxt(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                jdb = JsonDatabase('database')
                jdb.check_create()
                jdb.load()               
                getUser = jdb.get_user(update.message.sender.username)
                for f in files:
                    separator = ''
                    print(f)
                    host = f['directurl'].split('/draftfile')[0]+'/'
                    linkdraft = f['directurl'].split(host)[1]
                    token = '?token='+getUser['token']
                    urls = host+'webservice/'+linkdraft+token
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(urls+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                os.unlink(name)

def onmessage(update,bot:ObigramClient):
    try:
        thread = bot.this_thread
        username = update.message.sender.username

        #set in debug
        tl_admin_user = 'JAGB2021'

        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()

        user_info = jdb.get_user(username)

        if username == tl_admin_user or user_info:  # validate user
            if user_info is None:
                if username == tl_admin_user:
                    jdb.create_admin(username)
                else:
                    jdb.create_user(username)
                user_info = jdb.get_user(username)
                jdb.save()
        else:
            mensaje = "❌No tienes acceso❌\n📝Para ampliar su contrato\n👉Contactar a: @Zeta30\n"
            bot.sendMessage(update.message.chat.id,mensaje)
            return

        msgText = ''
        try: msgText = update.message.text
        except:pass

        # comandos de admin
        if '/add_user' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user(user)
                    jdb.save()
                    msg = '✅ @'+user+' has being added to the bot!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'⚠️Command error /add username')
            else:
                bot.sendMessage(update.message.chat.id,'👮You do not have administrator permissions👮')
            return

        if '/ban_user' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    if user == username:
                        bot.sendMessage(update.message.chat.id,'⚠️You can not ban yourself⚠️')
                        return
                    jdb.remove(user)
                    jdb.save()
                    msg = '𝚃𝚑𝚎 𝚞𝚜𝚎𝚛 @'+user+' 𝚑𝚊𝚜 𝚋𝚎𝚒𝚗𝚐 𝚋𝚊𝚗𝚗𝚎𝚍 𝚏𝚛𝚘𝚖 𝚝𝚑𝚎 𝚋𝚘𝚝!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'⚠️Command error /ban username⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'👮You do not have administrator permissions👮')
            return

        if '/get_db' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                database = open('database.jdb','r')
                bot.sendMessage(update.message.chat.id,database.read())
                database.close()
            else:
                bot.sendMessage(update.message.chat.id,'👮You do not have administrator permissions👮')
            return
        # end

        # comandos de usuario
        if '/help' in msgText:
            message = bot.sendMessage(update.message.chat.id,'📄Guía de Usuario:')
            tuto = open('tuto.txt','r')
            bot.sendMessage(update.message.chat.id,tuto.read())
            tuto.close()
            return

        if '/myuser' in msgText:
            getUser = user_info
            if getUser:
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return

        if '/zips' in msgText:
            getUser = user_info
            if getUser:
                try:
                   size = int(str(msgText).split(' ')[1])
                   getUser['zips'] = size
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = '🗜️Perfect now the zips will be of '+ sizeof_fmt(size*1024*1024)+' the parts📚'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'⚠️Command error /zips zips_size⚠️')    
                return

        if '/host' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                host = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_host'] = host
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Command error /host cloud_url⚠️')
            return

        if '/set_token' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                token = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['token'] = token
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    bot.sendMessage(update.message.chat.id,'😎Token guardado😎')
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Command error /host cloud_url⚠️')
            return

        if '/proxy' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                proxy = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['proxy'] = proxy
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '🧬Perfect, proxy equipped successfuly.'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'🧬Error equipping proxy.')
            return
                    
        if '/cancel_' in msgText:
            try:
                cmd = str(msgText).split('_',2)
                tid = cmd[1]
                tcancel = bot.threads[tid]
                msg = tcancel.getStore('msg')
                tcancel.store('stop',True)
                time.sleep(3)
                bot.editMessageText(msg,'❌Tarea cancelada❌')
            except Exception as ex:
                print(str(ex))
            return
        #end

        message = bot.sendMessage(update.message.chat.id,'🎐Analizando')

        thread.store('msg',message)

        if '/start' in msgText:
            start_msg = 'ⓘBienvenid@ @' + str(username)+'─〄\nSi necesitas ayuda usa /help\n'
            bot.editMessageText(message,start_msg)
        elif '/token' in msgText:
            message2 = bot.editMessageText(message,'🔮Obteniendo token🔮')

            try:
                proxy = ProxyCloud.parse(user_info['proxy'])
                client = MoodleClient(user_info['moodle_user'],
                                      user_info['moodle_password'],
                                      user_info['moodle_host'],
                                      user_info['moodle_repo_id'],proxy=proxy)
                loged = client.login()
                if loged:
                    token = client.userdata
                    modif = token['token']
                    bot.editMessageText(message2,'🔮Su token es:\n'+modif)
                    client.logout()
                else:
                    bot.editMessageText(message2,'⚠️The moodle '+client.path+' does not have token⚠️')
            except Exception as ex:
                bot.editMessageText(message2,'⚠️The moodle '+client.path+' does not have token or check out your account⚠️')       
        elif '/delete' in msgText:
            enlace = msgText.split('/delete')[-1]
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged= client.login()
            if loged:
                #update.message.chat.id
                deleted = client.delete(enlace)

                bot.sendMessage(update.message.chat.id, "Archivo eliminado con exito...")
        elif 'uptodown.com' in msgText:
            try:
                url = msgText
                bot.editMessageText(message,'📥 Descargando de uptodown 📥')
                file = uptodown.Download(url, output='')
                bot.editMessageText(message,'📥 Descarga finalizada 📥')
                processFile(update,bot,message,file,thread=thread,jdb=jdb)               
            except:
                bot.sendMessage(update.message.chat.id,'❌Error al descargar❌')                
        elif 'http' in msgText:
            url = msgText
            ddl(update,bot,message,url,file_name='',thread=thread,jdb=jdb)
        else:
            bot.editMessageText(message,'⚠️Error⚠️')
    except Exception as ex:
           print(str(ex))
  

def main():
    bot_token = '5947045568:AAE0mfkt85dPRAYIKGBEFdHd4qG4U3Y4bAA'
    

    bot = ObigramClient(bot_token)
    bot.onMessage(onmessage)
    bot.run()
    asyncio.run()

if __name__ == '__main__':
    try:
        main()
    except:
        main()
