from abc import ABCMeta, abstractmethod
# from time import sleep
from threading import Thread

from covertutils.helpers import defaultArgMerging
from covertutils.handlers import BaseHandler

import calendar, datetime, time


def __generateDays() :

	def day_data(i):
		dayname = calendar.day_name[i]
		return [i, str( i ), dayname, dayname.lower(), dayname[:3], dayname[:3].lower()]

	return {i: day_data(i) for i in range(7)}

days = __generateDays()
# print( days )

def getDay( inp ) :

	for k, v in days.items() :
		if inp in v :
			return k
	return False


#	From https://www.daniweb.com/programming/software-development/code/216721/calculate-easter-sunday-python
def calc_easter(year):
    """returns the date of Easter Sunday of the given yyyy year"""
    y = year
    # golden year - 1
    g = y % 19
    # offset
    e = 0
    # century
    c = y/100
    # h is (23 - Epact) mod 30
    h = (c-c/4-(8*c+13)/25+19*g+15)%30
    # number of days from March 21 to Paschal Full Moon
    i = h-(h/28)*(1-(h/28)*(29/(h+1))*((21-g)/11))
    # weekday for Paschal Full Moon (0=Sunday)
    j = (y+y/4+i+2-c+c/4)%7
    # number of days from March 21 to Sunday on or before Paschal Full Moon
    # p can be from -6 to 28
    p = i-j+e
    d = 1+(p+27+(p+6)/40)%31
    m = 3+(p+26)/30
    return datetime.date(y,m,d)


class DateableHandler (BaseHandler) :

	__metaclass__ = ABCMeta

	Defaults={
			'workinghours' : ( (9,0),(17,0) ),	# 9-17 shift
			'weekends' : [5, 6],	# Any input will do
			'holidays' : [
				(1,1), (25,12),		# Christmas and New Years Eve (day, month)
			],
			'easter' : {		# If set to False no Easter calculation gets done
				'before' : 2,
				'after' : 2,
			},
	}


	def __init__( self, recv, send, orchestrator, **kw ) :
		super(DateableHandler, self).__init__( recv, send, orchestrator, **kw )

		arguments = defaultArgMerging( self.Defaults, kw )
		self.dates = {}
		self.dates['workinghours'] = arguments['workinghours']
		self.dates['weekends'] = []
		for day in arguments['weekends'] :
			normalized_day = getDay(day)
			self.dates['weekends'].append( normalized_day )	# Store days as 0-6 numbers only
		self.dates['holidays'] = arguments['holidays']
		self.dates['easter'] = arguments['easter']



	def _isItWorkingHours( self, obj ) :	# Could also make 2 datetime objects
		now_time = obj.time()
		# Taken from: https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
		shift_start = datetime.time( *self.dates['workinghours'][0] )
		shift_end = datetime.time( *self.dates['workinghours'][1] )
		if shift_start <= now_time <= shift_end :
			return True		# TODO: make it crossing modnight
		return False


	def _isItHoliday( self, obj ) :
		current_month = obj.month
		current_day = obj.day
		for hol_day, hol_month in self.dates['holidays'] :	# DD/MM
			if hol_month == current_month and hol_day == current_day :
				return True
		return False


	def _isItWeekend( self, obj ) :
		current_weekday = obj.weekday()
		if current_weekday in self.dates['weekends'] :
			return True
		return False


	def _isItEasterHoliday( self, date_obj ) :
		if not self.dates['easter'] : return False
		year = date_obj.year
		date_date_obj = date_obj.date()
		easter_obj = calc_easter(year)
		days_after_easter = (date_date_obj - easter_obj).days
		days_before_easter = (easter_obj - date_date_obj).days
		if 0 <= days_after_easter <= self.dates['easter']['after']  :
			return True
		if 0<= days_before_easter <= self.dates['easter']['before'] :
			return True
		return False


	def mustNotRespond( self, fixed_date = None ) :
		now_obj = fixed_date or datetime.datetime.now()

		if self._isItEasterHoliday( now_obj ) :
			print( "Easter Block" )
			return True

		if not self._isItWorkingHours( now_obj ) :
			print( "Working Hours Block" )
			return True

		if self._isItWeekend( now_obj ) :
			print( "Weekend Block" )
			return True

		if self._isItHoliday( now_obj ) :
			print( "Holiday Block" )
			return True

		return False


	def sendAdHoc( self, message, stream = None ) :
		if self.mustNotRespond() :
			return False
		return super(BaseHandler, self).sendAdHoc( message, stream )


	def queueSend( self, message, stream = None ) :
		if self.mustNotRespond() :
			return False
		return super(BaseHandler, self).queueSend( message, stream )
