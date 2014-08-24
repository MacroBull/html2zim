#!/usr/bin/env python
# @author: macrobull
# @Github: https://github.com/MacroBull/html2zim

from HTMLParser import HTMLParser

import os
import sys
import re

imgDownTool = None
imgDownaPath = None

def url2local(url):
	for s in [':', '/']:
		url = url.replace(s, '_')
	return url[-128:]

class Html2ZimParser(HTMLParser):
	def __init__(self):
		self._zim = ''
		self._ol_depth = -1
		self._ul_depth = -1
		self._tag_stack = []
		self._tag_attr_data = {}
		self._text = ''
		self._zim = ''
		#self._convertible_tags = ['a',
								  #'b', 'blockquote',
								  #'em',
								  #'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr',
								  #'ol',
								  #'p', 'pre',
								  #'strong',
								  #'u',
								  #'strike',
								  #'code',
								  #'img',
								  #'input',
								  #'ul']
		# FIXME: special characters
		HTMLParser.__init__(self)

	def _append_to_zim(self):
		self._zim += self._text
		self._text = ''


	######################links#################################
	# <a /> Zim do not support format in url discriptions
	def handle_start_a(self, attrs):
		self._attrs = attrs
#		url = dict(attrs).get('href')
#		if url.startswith('/'):
#			url = url.replace('/', ':')
#		elif url.startswith('./'):
#			url = '+' + url[1:].replace('/', ':')
#		elif url.startswith('../'):
#			url = url[3:].replace('/', ':')
#		self._text += '[[' + url
#		self._append_to_zim()

	def handle_end_a(self):
		url = dict(self._attrs).get('href')
		if url.startswith('/'):
			url = url.replace('/', ':')
		elif url.startswith('./'):
			url = '+' + url[1:].replace('/', ':')
		elif url.startswith('../'):
			url = url[3:].replace('/', ':')
		disc = self._text
		if disc:
			disc = ' | '+ disc
		self._text += '[[' + url + disc + ']]'
		self._append_to_zim()

	'''
	#<img />
	def handle_end_img(self):
		img_tag = ''
		ref = self._tag_attr_data.get('href')
		if ref:
			img_tag += '[[' +self._tag_attr_data.get('href')
			title = self._tag_attr_data.get('title')
			if title:
				img_tag += ' | '+ title
			img_tag += ']] '
		img_tag += '{{' + self._tag_attr_data.get('src') + '}}'

		self._append_to_zim(img_tag)
	'''

	#<img />
	def handle_start_img(self, attr):
		img_tag = ''
		attr = dict(attr)
		src = attr.get('src')
		if src and imgDownTool and re.match('.*tp.*://.*', src): # valid full URL
			img_tag += '{{' + imgDownaPath + '/' + url2local(attr['src']) + '}}'
			if imgDownTool == 'wget':
				os.popen2('wget "' + src + '" -O "' + imgDownaPath + '/' + url2local(attr['src']) +'" 2>/dev/null')
			elif imgDownTool == 'kio':
				os.popen2('kioclient copy --overwrite "' + src + '" "' + imgDownaPath + '/' + url2local(attr['src']) +'" 2>/dev/null')
		if attr.has_key('href'):
			img_tag += os.linesep + '[[' + attr['href']
			if attr.has_key('title'):
				img_tag += ' | '+ attr['title']
			img_tag += ']] '

		self._text += img_tag
		self._append_to_zim()

	def handle_end_img(self):
		img_tag = ''
		ref = self._tag_attr_data.get('href')
		src = self._tag_attr_data.get('src')
		if src and imgDownTool and re.match('.*tp.*://.*', src): # valid full URL
			img_tag += '{{' + imgDownaPath + '/' + url2local(src) + '}}'
			if imgDownTool == 'wget':
				os.popen2('wget "' + src + '" -O "' + imgDownaPath + '/' + url2local(attr['src']) +'" 2>/dev/null')
			elif imgDownTool == 'kio':
				os.popen2('kioclient copy --overwrite "' + src + '" "' + imgDownaPath + '/' + url2local(attr['src']) +'" 2>/dev/null')
		if ref:
			img_tag += os.linesep +'[[' +self._tag_attr_data.get('href')
			title = self._tag_attr_data.get('title')
			if title:
				img_tag += ' | '+ title
			img_tag += ']] '
		self._text += img_tag
		self._append_to_zim()


	######################headers#################################

	# <h1 />
	def handle_end_h1(self):
		self._text = os.linesep + '====== ' + self._text.replace(os.linesep, ' ') + ' ======' + os.linesep
		self._append_to_zim()

	# <h2 />
	def handle_end_h2(self):
		self._text = os.linesep + '===== ' + self._text.replace(os.linesep, ' ') + ' =====' + os.linesep
		self._append_to_zim()

	# <h3 />
	def handle_end_h3(self):
		self._text = os.linesep + '==== ' + self._text.replace(os.linesep, ' ') + ' ====' + os.linesep
		self._append_to_zim()

	# <h4 />
	def handle_end_h4(self):
		self._text = os.linesep + '=== ' + self._text.replace(os.linesep, ' ') + ' ===' + os.linesep
		self._append_to_zim()

	# <h5 />
	def handle_end_h5(self):
		self._text = os.linesep + '== ' + self._text.replace(os.linesep, ' ') + ' ==' + os.linesep
		self._append_to_zim()

	# <h6 />
	def handle_end_h6(self):
		self._text = os.linesep + '####' + self._text.replace(os.linesep, ' ') + ' ####' + os.linesep
		self._append_to_zim()


	######################widgets#################################

	# <li />
	def handle_start_li(self, attrs):
		if len(self._tag_stack):
			if self._tag_stack[-1] == 'ol':
				order = 'a.	' if (self._ol_depth & 1) else '1.	'
				self._text += '\t' * self._ol_depth + order
			else:
				self._text += '\t' * self._ul_depth + '*	'
		self._append_to_zim()



	def handle_end_li(self):
		self._text += os.linesep
		self._append_to_zim()


	def handle_start_ol(self, attrs):
		self._ol_depth +=1

	def handle_end_ol(self):
		self._ol_depth -=1

	def handle_start_ul(self, attrs):
		self._ul_depth +=1

	def handle_end_ul(self):
		self._ul_depth -=1

	# checkbox <input>
	def handle_start_input(self, attr):
		input_tag = ''
		attr = dict(attr)
		if attr['type'] == "checkbox":
			if attr.has_key("checked") and attr['type'] == "checkbox":
				input_tag +='[*] '
				#input_tag +='[x] '
			else:
				input_tag +='[ ] '
		self._text += input_tag
#		self._append_to_zim()
#
#	def handle_end_input(self):
#		self._append_to_zim(self._text + os.linesep)



	######################text formats#################################
	# <br>
	def handle_start_br(self, attr):
		self._text += os.linesep

	# <span />
	def handle_end_span(self):
		self._append_to_zim()

	# <p />
	def handle_end_p(self):
		self._append_to_zim()

	# <b />
	def handle_start_b(self, attr):
		self._text += '**'
		self._append_to_zim()

	def handle_end_b(self):
		self._text += '**'
		self._append_to_zim()
	# <strong />
	handle_start_strong = handle_start_b
	handle_end_strong = handle_end_b


	# <pre />
	def handle_start_pre(self, attr):
		self._text += "''"
		self._append_to_zim()

	def handle_end_pre(self):
		self._text += "''"
		self._append_to_zim()

	# <code />
	def handle_start_code(self, attr):
		self._text += os.linesep + "'''"  + os.linesep
		self._append_to_zim()

	def handle_end_code(self):
		self._text += os.linesep + "'''"  + os.linesep + os.linesep
		self._append_to_zim()

	# <blockquote />
	handle_start_blockquote = handle_start_code
	handle_end_blockquote = handle_end_code


	# <i />
	def handle_start_i(self, attr):
		self._text += '//'
		self._append_to_zim()

	def handle_end_i(self):
		self._text += '//'
		self._append_to_zim()

	# <em />
	handle_start_em = handle_start_i
	handle_end_em = handle_end_i


	# <u />
	def handle_start_u(self, attr):
		self._text += '__'
		self._append_to_zim()

	def handle_end_u(self):
		self._text += '__'
		self._append_to_zim()

	# <strike />
	def handle_start_strike(self, attr):
		self._text += '~~'
		self._append_to_zim()

	def handle_end_strike(self):
		self._text += '~~'
		self._append_to_zim()

	#<del />
	handle_start_del = handle_start_strike
	handle_end_del = handle_end_strike


	#######################Kernel################################
	def handle_starttag(self, tag, attrs):
		self._tag_stack.append(tag)
		try:
			eval('self.handle_start_' + tag + '(attrs)')
		except AttributeError, e:
			pass

	def handle_endtag(self, tag):
		self._tag_stack.pop()
		try:
			eval('self.handle_end_' + tag + '()')
			# Collapse three successive CRs into two before moving on
			while len(self._zim) > 2 and \
					self._zim[-3:] == '%s%s%s' % (os.linesep, os.linesep, os.linesep):
				self._zim = self._zim[:-3] + '%s%s' % (os.linesep, os.linesep)
		except AttributeError, e:
			pass

		self._tag_attr_data = {}
		self._text = ''

	def handle_data(self, data):
		#data = os.linesep.join(map(string.strip, data.strip().split(os.linesep)))
		self._text += data
		if not(len(self._tag_stack) and self._tag_stack[-1] not in ['p']):
			self._append_to_zim()

	def get_zim(self):
		return self._zim.rstrip() + os.linesep

def main():
	global imgDownTool, imgDownaPath

	try:
		paridx = sys.argv.index('-w')
		imgDownTool = 'wget'
		imgDownaPath = sys.argv.pop(paridx +1)
		sys.argv.pop(paridx)
	except ValueError, e:
		imgDownTool = None

	try:
		paridx = sys.argv.index('-k')
		imgDownTool = 'kio'
		imgDownaPath = sys.argv.pop(paridx +1)
		sys.argv.pop(paridx)
	except ValueError, e:
		imgDownTool = None

	if imgDownaPath:
		os.popen('mkdir -p '+ imgDownaPath)

	p = Html2ZimParser()
	if len(sys.argv)>1:
		buf = open(sys.argv[1]).read()
	else:
		buf = sys.stdin.read().decode('utf-8')
	p.feed(buf)
	p.close()
	print p.get_zim().encode('utf-8')

if __name__ == "__main__":
	sys.exit(main())