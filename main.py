import sys
import os
import sqlite3
import hashlib
import datetime

if __name__ == "__main__":
	operation = ""
	recordType = ""
	filename = ""
	inputFileData = ""
	filedataline = ""
	fileData = []
	fileDataItem = []

	try:
		operation = sys.argv[1]
	except:
		print "Usage: ", sys.argv[0], " <operation> <type> <file> [options]"
		print "operation must be \"import\" or \"export\""
		exit(-1)
	if operation != "import" and operation != "export":
		exit(-1)

	try:
		recordType = sys.argv[2]
	except:
		print "Usage: ", sys.argv[0], " <operation> <type> <file> [options]"
		print "operation must be \"import\" or \"export\""
		exit(-1)

	try:
		filename = sys.argv[3]
	except:
		print "Usage: ", sys.argv[0], " <operation> <type> <file> [options]"
		print "operation must be \"import\" or \"export\""
		exit(-1)

	conn = sqlite3.connect('db.sqlite')
	#conn.isolation_level = None
	c = conn.cursor()
	c.execute("create table if not exists importedfiles(id integer primary key autoincrement, filename text, hashmd5 text, hashsha1 text, importtime text)")
	c.execute("create table if not exists dict(id integer primary key autoincrement, type text, word text, counter integer)")

	if operation == "import":
		if recordType != "username" and recordType != "password" and recordType != "other":
			exit(-1)
		if os.path.exists(filename):
			with open(filename, "r") as inputFile:
				c.execute("select filename from importedfiles where filename = ?", (os.path.basename(filename),))
				row = c.fetchone()
				if row != None:
					print "There is a imported file named ", os.path.basename(filename)
					print "Do you want to continue?[Y/N]",
					inputCh = raw_input()
					if inputCh == "Y" or inputCh == "y":
						pass
					else:
						exit(0)

				inputFileData = inputFile.read()
				inputFile.seek(0)
				md5obj = hashlib.md5()
				sha1obj = hashlib.sha1()
				md5obj.update(inputFileData)
				sha1obj.update(inputFileData)
				md5hash = md5obj.hexdigest()
				sha1hash = sha1obj.hexdigest()

				c.execute("select id, filename from importedfiles where hashmd5 = ? and hashsha1 = ?", (md5hash, sha1hash))
				row = c.fetchone()
				if row == None:
					c.execute("insert into importedfiles(filename, hashmd5, hashsha1, importtime) values(?, ?, ?, ?)", (os.path.basename(filename), md5hash, sha1hash, datetime.datetime.now()))
				else:
					print "The same file has been imported!"
					exit(0)

				while(True):
					filedataline = inputFile.readline()
					if not filedataline:
						break
					filedataline = filedataline.strip()
					fileData.append(filedataline)
					filedataline = ""
				fileDataItem = sorted(list(set(fileData)))

				newImportSequence = []
				importSequence = []
				for item in fileDataItem:
					c.execute("select counter from dict where type = ? and word = ?", (recordType, item))
					row = c.fetchone()
					if row == None:
						newImportSequence.append((recordType, item, fileData.count(item)))
					else:
						importSequence.append((int(row[0]) + fileData.count(item), recordType, item))

				if newImportSequence:
					c.executemany("insert into dict(type, word, counter) values(?, ?, ?)", newImportSequence)
				if importSequence:
					c.executemany("update dict set counter = ? where type = ? and word = ?", importSequence)

				conn.commit()
		else:
			print "Import file does not exist!"
			exit(-1)
	elif operation == "export":
		if recordType != "all" and recordType != "username" and recordType != "password" and recordType != "other":
			exit(-1)
		with open(filename, "w") as outputFile:
			pass
	else:
		print "Wrong operation!"
		exit(-1)

	conn.close()
