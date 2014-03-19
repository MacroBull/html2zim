#!/usr/bin/env python

from HTMLParser import HTMLParser

import re
import os
import sys
import string

class Html2ZimParser(HTMLParser):
	def __init__(self):
		self._zim = ''
		self._ol_depth = -1
		self._ul_depth = -1
		self._tag_stack = []
		self._tag_attr_data = {}
		self._handled_tag_body_data = ''
		self._convertible_tags = ['a',
								  'b', 'blockquote',
								  'em',
								  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr',
								  'ol',
								  'p', 'pre',
								  'strong',
								  'u',
								  'strike',
								  'code',
								  'img',
								  'input',
								  'ul']
		# FIXME: special characters
		HTMLParser.__init__(self)

	def _append_to_zim(self, new_zim):
		if len(self._zim) > 1:
			if re.match('\s', self._zim[-1:]):
				self._zim += new_zim
			else:
				self._zim += ' ' + new_zim
		else:
			self._zim += new_zim

	# <a />
	def handle_start_a(self, attrs):
		self._tag_attr_data = dict(attrs)

	def handle_end_a(self):
		a_tag = ''
		a_tag += '[[' + self._tag_attr_data.get('href') +' | '+ self._handled_tag_body_data + ']]'
		'''
		a_tag += '(' + 

		title = self._tag_attr_data.get('title')
		if title:
			a_tag += ' "' + title + '") '
		else:
			a_tag += ') '
		'''
		self._append_to_zim(a_tag)
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
	
	#<img>
	def handle_start_img(self, attr):
		img_tag = ''
		attr = dict(attr)
		if attr.has_key('href'):
			img_tag += '[[' + attr['href']
			if attr.has_key('title'):
				img_tag += ' | '+ attr['title']
			img_tag += ']] '
		img_tag += '{{' + attr['src'] + '}}'
		
		self._append_to_zim(img_tag)
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

	# <b />
	def handle_end_b(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('*' + self._handled_tag_body_data + '*')

	# <blockquote />
	def handle_end_blockquote(self):
		blockquote_body = self._handled_tag_body_data.split(os.linesep)

		for blockquote_line in blockquote_body:
			blockquote_line = blockquote_line.strip()
			self._append_to_zim('> ' + blockquote_line + os.linesep)

	# <em />
	def handle_end_em(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('//' + self._handled_tag_body_data + '//')
	
	# <u />
	def handle_end_u(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('__' + self._handled_tag_body_data + '__')
	
	# <code />
	def handle_end_code(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim("''" + self._handled_tag_body_data + "''")
	
	# <strike />
	def handle_end_strike(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('~~' + self._handled_tag_body_data + '~~')

	# <h1 />
	def handle_end_h1(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('====== ' + self._handled_tag_body_data + ' ======' + os.linesep)

	# <h2 />
	def handle_end_h2(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('===== ' + self._handled_tag_body_data + ' =====' + os.linesep)

	# <h3 />
	def handle_end_h3(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('==== ' + self._handled_tag_body_data + ' ====' + os.linesep)

	# <h4 />
	def handle_end_h4(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('=== ' + self._handled_tag_body_data + ' ===' + os.linesep)

	# <h5 />
	def handle_end_h5(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('== ' + self._handled_tag_body_data + ' ==' + os.linesep)

	# <h6 />
	def handle_end_h6(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('###### ' + self._handled_tag_body_data + ' ######' + os.linesep)

	# <hr />
	def handle_start_hr(self, attrs):
		self._append_to_zim('* * *' + os.linesep)

	# <li />
	def handle_end_li(self):
		if len(self._tag_stack):
			if self._tag_stack[-1] == 'ol':
				order = 'a.	' if (self._ol_depth & 1) else '1.	'
				self._append_to_zim('\t' * self._ol_depth + order + self._handled_tag_body_data + os.linesep)
			elif self._tag_stack[-1] == 'ul':
				self._append_to_zim('\t' * self._ul_depth + '*	' + self._handled_tag_body_data + os.linesep)

	
	def handle_start_ol(self, attrs):
		self._ol_depth +=1
		
	def handle_end_ol(self):
		self._ol_depth -=1
		
	def handle_start_ul(self, attrs):
		self._ul_depth +=1
		
	def handle_end_ul(self):
		self._ul_depth -=1
	
	
	def handle_start_input(self, attr):
		input_tag = ''
		attr = dict(attr)
		if attr['type'] == "checkbox":
			input_tag +='[ ] '
		self._append_to_zim(input_tag)
	
	def handle_end_input(self):
		self._append_to_zim(self._handled_tag_body_data + os.linesep)
	
	# <p />
	def handle_start_p(self, attrs):
		if len(self._zim) > 1:
			if self._zim[-2:] == '%s%s' % (os.linesep, os.linesep):
				pass
			elif self._zim[-1:] == os.linesep:
				self._zim += os.linesep
			else:
				self._zim += os.linesep + os.linesep

	def handle_end_p(self):
		self._zim += '%s%s' % (os.linesep, os.linesep)

	# <pre />
	def handle_end_pre(self):
		self._append_to_zim("'''" + os.linesep + self._handled_tag_body_data + os.linesep + "'''" + os.linesep)

	# <strong />
	def handle_end_strong(self):
		self._handled_tag_body_data = self._handled_tag_body_data.replace(os.linesep, ' ')
		self._append_to_zim('**' + self._handled_tag_body_data + '**')

	## ###
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
		self._handled_tag_body_data = ''

	def handle_data(self, data):
		#data = os.linesep.join(map(string.strip, data.strip().split(os.linesep)))
		if len(self._tag_stack) and self._tag_stack[-1] not in ['p']:
			self._handled_tag_body_data += data
		else:
			self._append_to_zim(data)

	def get_zim(self):
		return self._zim.rstrip() + '\n'

def main():
	p = Html2ZimParser()
	buf = sys.stdin.read().decode('utf-8')
	p.feed(buf)
	p.close()
	print p.get_zim().encode('utf-8')

if __name__ == "__main__":
	sys.exit(main())