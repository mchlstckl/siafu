# This Python file uses the following encoding: utf-8

from fabric.api import *
from fabric.contrib.console import *
from fabric.contrib.files import *

import yaml
import time
import random
import cmd


dry_run = False


def _execute(ops):
	for c, ms in ops:
		print "---> ", c, ms
		if dry_run:
			continue
		if c.startswith('~'):
			eval(c[1:])
		else:
			for m in ms:
				with settings(host_string=m):
					sudo(c)


def _process_actions(context, actions):
	services = context['services']
	machines = context['machines']
	ops = []
	for a in actions:
		op, rem = a.split(' ', 1)
		if (op in ['start', 'stop']):
			sm = rem.split(' ')
			name = sm[0]
			service, ms = services[name]
			if len(sm) > 1:
				ops.append(( 'service %s %s' % (service, op), [ machines[sm[1]] ] ))
			else:
				ops.append(( 'service %s %s' % (service, op), [ machines[m] for m in ms ] ))
		elif op == 'shutdown':
			ops.append(( 'shutdown now', [ machines[rem] ] ))
		elif op == 'reboot':
			ops.append(( 'reboot', [ machines[rem] ] ))
		elif op == 'wait':
			ops.append(( '~time.sleep(%s)' % rem, None ))
		elif op.startswith('$'):
			ms = [ machines[m] for m in op[1:].split(',') ]
			ops.append(( rem, ms ))
		elif op.startswith('^'):
			service, ms = services[op[1:]]
			ops.append(( rem, [ machines[m] for m in ms ] ))
	_execute(ops)


def _process_settings(settings_file):
	f = open(settings_file)
	context = yaml.load(f)
	f.close()

	machines = context['machines']

	services = dict()
	for s in context['services']:
		services[s['name']] = (s['service'], s['machines'])

	scenarios = dict()
	for s in context['scenarios']:
		scenarios[s['name']] = s['actions']

	return { 'machines': machines, 'services': services, 'scenarios': scenarios }


def start(settings_file='siafu.yaml', scenario=None):
	'''
	Run me with fabric: fab -f siafu.py start:scenario
	'''
	context = _process_settings(settings_file)
	if not scenario == None:
		_process_actions(context, context['scenarios'][scenario])


def _print_info(context):
	print """
	 ____ _____ _____ _____ _____
	|   __|     |  _  |   __|  |  |
	|__   |-   -|     |   __|  |  |
	|_____|_____|__|__|__|  |_____|
	  Siafu: Anarchist Ant Army"""

	print "\nCommands:"
	print "  $<machines> <shell command>\t e.g. $m01,m02 mkdir /tmp/test"
	print "  ^<service> <shell command> \t e.g. ^apache2 mkdir /tmp/test"
	print "  start <service> [machine]  \t e.g. start apache2 m01"
	print "  stop <service> [machine]   \t e.g. stop apache2 m01"
	print "  reboot <machine>           \t e.g. reboot m01"
	print "  shutdown <machine>         \t e.g. shutdown m01"
	print "  do <scenario>              \t e.g. do kill journals"
	print "  anarchy [delay]: run random scenarios"
	print "  d: toggle dry-run (%s)" % dry_run
	print "  w: toggle warn-only (%s)" % env.warn_only
	print "  ?: show this"
	print "  q: quit console"

	print "\nScenarios:"
	for k, v in context['scenarios'].iteritems():
		print ' ', k, v

	print "\nServices:"
	for k, (s, ms) in context['services'].iteritems():
		print ' ', k, '→', s, '@', ms

	print "----------------------"


def _anarchy(context, delay):
	scenarios = context['scenarios']
	print "Start of anarchy!"
	while True:
		try:
			name, actions = random.choice(scenarios.items())
			print name, actions
			_process_actions(context, actions)
			print "Wait %ss" % delay
			time.sleep(delay)
		except KeyboardInterrupt:
			print "End of anarchy"
			break


@task(default=True)
def menu(settings_file='siafu.yaml'):
	'''
	Run me with fabric: fab -f siafu.py menu
	'''
	context = _process_settings(settings_file)
	console = Console(context)
	console.cmdloop()


class Console(cmd.Cmd):

	def __init__(self, context):
		cmd.Cmd.__init__(self)
		self.context = context
		self.prompt = "siafu ☷  "
		self.do_help(None)

	def emptyline(self):
		self.do_help(None)

	def do_q(self, args):
		print "Good-bye"
		return -1

	def do_EOF(self, args):
		return self.do_quit(args)

	def do_help(self, args):
		_print_info(self.context)

	def do_d(self, args):
		global dry_run
		dry_run = not dry_run
		print "dry-run =", dry_run

	def do_w(self, args):
		env.warn_only = not env.warn_only
		print "warn-only =", env.warn_only

	def do_anarchy(self, args):
		delay = float(args) if args else 2
		_anarchy(self.context, delay)

	def do_do(self, args):
		actions = self.context['scenarios'][args]
		_process_actions(self.context, actions)

	def complete_do(self, text, line, begidx, endidx):
		scenarios = self.context['scenarios'].keys()
		offset = len('do ')
		start = begidx - offset
		search = line[offset:]
		match = lambda x: x.startswith(search)
		crop = lambda x: x[start:]
		results = filter(match, scenarios)
		return map(crop, results)
		
	def default(self, args):
		_process_actions(self.context, [args])
