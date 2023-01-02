from pyobigram.utils import sizeof_fmt,nice_time
import datetime
import time
import os

def text_progres(index,max):
	try:
		if max<1:
			max += 1
		porcent = index / max
		porcent *= 100
		porcent = round(porcent)
		make_text = ''
		index_make = 1
		make_text += '['
		while(index_make<21):
			if porcent >= index_make * 5: make_text+='▣'
			else: make_text+='□'
			index_make+=1
		make_text += ']'
		return make_text
	except Exception as ex:
			return ''

def porcent(index,max):
    porcent = index / max
    porcent *= 100
    porcent = round(porcent)
    return porcent

def createDownloading(filename,totalBits,currentBits,speed,time,tid=''):
    msg = "🔻Descargando archivo🔻\n"
    msg += text_progres(currentBits, totalBits) + "\n"
    msg += "👉"+filename+'\n'
    msg += "🔻Descargado: "+sizeof_fmt(currentBits) + ' de ' + sizeof_fmt(totalBits) + '\n'
    msg += "⚡️Speed: "+sizeof_fmt(speed)+'/s ''| ''⏰𝐄𝐓𝐀: '+str(datetime.timedelta(seconds=int(time)))+'s\n'
    if tid!='':
        msg+= '❌/cancel_' + tid
    return msg

def createUploading(filename,totalBits,currentBits,speed,time,originalname=''):
    msg = "🔺Subiendo Archivo🔺\n"
    msg += text_progres(currentBits, totalBits) + "\n"
    msg += "👉"+filename+"\n"
    msg += "📤Subido: "+sizeof_fmt(currentBits) + ' de ' + sizeof_fmt(totalBits) + '\n'
    msg += "⚡️Speed: "+sizeof_fmt(speed)+'/s ''| ''⏰𝐄𝐓𝐀: '+str(datetime.timedelta(seconds=int(time)))+'s\n\n'
    return msg

def createCompresing(filename,filesize,splitsize):
    msg  = "🗜️Comprimiendo Archivo\n\n"
    msg += "🗜Comprimiendo "+ str(round(int(filesize/splitsize)+1,1))+" en partes de "+str(sizeof_fmt(splitsize))+'\n\n'
    return msg

def createFinishUploading(filename,filesize,urls,username):
    msg = "🔺Subida finalizada🔺\n"
    msg += "👉"+ str(filename)+"\n"
    msg += "🔗Enlance de descarga:\n"
    msg += urls+"\n"
    msg += "⚡️¡Siempre su mejor opción!⚡️\n"
    return msg

def createStatt(username,userdata,isadmin):
    from pyobigram.utils import sizeof_fmt
    msg = "👥 Usuario: "+str(userdata['moodle_user'])+'\n'
    msg += "🔑 Contraseña: "+str(userdata['moodle_password'])+'\n'
    msg += "☁️Página: "+ str(userdata['moodle_host'])+'\n'
    msg += "🗜Tamaño por archivo: "+ sizeof_fmt(userdata['zips']*1024*1024) + '\n\n'
    proxy = '❌'
    if userdata['proxy'] !='':
       proxy = '✅'
    msg += "🔌 Proxy: " + proxy +"\n"
    msgAdmin = '❌'
    if isadmin:
        msgAdmin = '✅'
    msg+= '🦾Admin : ' + msgAdmin + '\n\n'
    
    return msg

def createStat(username,userdata,isadmin):
    from pyobigram.utils import sizeof_fmt
    msg = "🗜️Zips: "+ sizeof_fmt(userdata['zips']*1024*1024) + '\n'
    msgAdmin = '❌'
    if isadmin:
        msgAdmin = '✅'
    msg+= '🔺Administrador: ' + msgAdmin + '\n\n'    
    return msg