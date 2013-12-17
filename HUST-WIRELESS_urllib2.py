#!/usr/bin/python
# -*- coding:utf-8 -*-
#请求testurl时返回的结果：<script>self.location.href='http://192.168.50.3:8080/eportal/index.jsp?wlanuserip=10.10.65.161&wlanacname=Ac_001aa97cd237&ssid=HUST_WIRELESS&nasip=192.168.8.2&mac=8ca98296eb3c&t=wireless-v2-plain&url=http://www.baidu.com/'</script>
#post_url:http://192.168.50.3:8080/eportal/index.jsp
#host_url:http://192.168.50.3:8080/
#query_args:wlanuserip=10.10.65.161&wlanacname=Ac_001aa97cd237&ssid=HUST_WIRELESS&nasip=192.168.8.2&mac=8ca98296eb3c&t=wireless-v2-plain&url=http://www.baidu.com/
#form_data:username=''&pwd=''&validcode=no_check&phone=&authorizationCode=&regist_validcode=&phonenum=&regist_validcode_sm=
#发起登陆请求后获得的参数:&mac=1b703f4248eeb581fb7481db4605ea07&wlanuserip=e6d6380107b5536d9c202a5f773fa925&nasip=8df3b80e79b397a516656c1e9cf9cb08&t=wireless-v2-plain&username=yy232381&url=http://www.baidu.com/
#下线时请求的url:host_url+logout_url+&mac=1b703f4248eeb581fb7481db4605ea07&wlanuserip=e6d6380107b5536d9c202a5f773fa925&nasip=8df3b80e79b397a516656c1e9cf9cb08
import re
import os 
import sys
import base64
import getpass
import urllib2

usr_id,psw,save_psw = '','',False
session_file = '.HUST_WIRELESS.session'
usr_file = '.HUST_WIRELESS.usr'
test_url = 'http://www.baidu.com/'
login_url = '/eportal/userV2.do?method=login'
login_args = '&param=true&fromHtml=true&userAgentForLogin=0&'
logout_url = '/eportal/userV2.do?method=logout'

#handle sys
if os.path.exists(usr_file):
	#read usr_info if had
	usr_id,psw = base64.decodestring(open(usr_file).read()).split(',')
	if psw != '':
		save_psw = True

if len(sys.argv)>1:
	if sys.argv[1]=='help' or sys.argv[1]=='-h' or sys.argv[1]=='--help':
		#help message
		print('Args:\t-s\tSave password (username is automatically saved)\n\t-c\tClean saved username and password\nNotes:\tSaved pswd is only softly protected, be cautious!\n\tCLI input overrides saved account.')
		os._exit(0)	
	if len(sys.argv) == 2 and sys.argv[1].startswith('-'):
		if 's' in sys.argv[1]: #save
			save_psw = True
		if 'c' in sys.argv[1]:	#clear
			if os.path.exists(usr_file):
				os.remove(usr_file)
				print('Account Info clear!')
			else:
				print('No Account Info')
	if len(sys.argv)>2 and sys.argv[1].startswith('-'):#judge if -u or -p
		if 'u' in sys.argv[1]:
			if usr_id != sys.argv[2]: #new usr
				psw = ''	#clear psw
				usr_id = sys.argv[2]
			if len(sys.argv)>4:
				if 'p' in sys.argv[3]:
					psw = sys.argv[4]
				else:
					psw = ''
		if 'p' in sys.argv[1]:
			if sys.argv[2]:
				psw = sys.argv[2]
			else:
				psw = ''
#test url
tt = urllib2.urlopen(test_url).read();
urls = re.findall('self.location.href=\'([^\']+)\'',tt)#get jump url
#logout
if not urls:#has connected to Internet
	#read session file
	if not os.path.exists(session_file):
		print('You\'ve connected to Internet, but it seems you are not using HUST-WIRELESS ?')
	else:
		host_url,args = open(session_file,'r').read().split(',')
		res = urllib2.urlopen('%s%s%s'%(host_url,logout_url,args)).read()
		if re.search('window.location.replace\("\./userV2\.do\?method=goToLogout"',res):
			print('Logout success!ByeBye')
			if os.path.exists(session_file):
				os.remove(session_file)
		else:
			print('Logout failed')
else:
	url = urls[0]
	post_url,query_args = url.split('?') #get host and args
	host_url = post_url.replace('/eportal/index.jsp','')#host_ip
	usr_id = usr_id or raw_input('username:')
	psw = psw or getpass.getpass('password for %s:'%usr_id)
	
	#build formdata
	formdata = 'username=%s&pwd=%s&validcode=no_check&phone=&authorizationCode=&regist_validcode=&phonenum=&regist_validcode_sm='%(usr_id,psw)

	#post
	#print '%s%s%s%s'%(host_url,login_url,login_args,query_args)
	req = urllib2.Request('%s%s%s%s'%(host_url,login_url,login_args,query_args))
	res = urllib2.urlopen(req,formdata).read() #response text
	addrargs = re.findall('window.location.replace\("\.\/userV2\.do\?method=goToAuthResult(&mac=.+&wlanuserip=.+&nasip=.+)',res)# check if login success and get login info
	if addrargs:
		print('Login succeed!')
		#save psw usr in usr_file
		open(usr_file,'w').write(base64.encodestring(','.join([usr_id,save_psw and psw or ''])))
		open(session_file,'w').write(','.join([host_url,addrargs[0]]))
	else:
		errmsg = re.findall('errorMessage.innerHTML = \'<strong>(.+)</strong>',res)
		print('Login failed: %s'%errmsg[0])

if len(sys.argv) == 1:
	raw_input('Press Enter to exit...')




		

