from __future__ import absolute_import, unicode_literals

from datetime import datetime
from django.core.management import call_command
from django.utils import timezone
from django.utils.six import StringIO
import pytest
from .factories import SouvenirFactory


@pytest.mark.django_db
class TestShowUsage:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.tzinfo = timezone.get_current_timezone()
        self.subscription_start = datetime(
            year=2010, month=1, day=24, hour=22, tzinfo=self.tzinfo)
        self.souvenirs = [
            SouvenirFactory(when=datetime(year=i, month=2, day=14,
                                          hour=12, tzinfo=self.tzinfo))
            for i in range(2010, 2018)
        ]
        self.souvenirs.append(
            SouvenirFactory(when=datetime(year=2015, month=10, day=17,
                                          hour=12, tzinfo=self.tzinfo))
        )

    def test_show_usage_daily(self):
        out = StringIO()
        call_command('show_usage', '--daily',
                     '--subscription-start={:%Y-%m-%d}'.format(
                         self.subscription_start),
                     '--before=3/8/2010',
                     stdout=out)
        assert out.getvalue().split() == '''
            date          registered    activated    active
            ----------  ------------  -----------  --------
            2010-03-08             1            1         0
            2010-03-07             1            1         0
            2010-03-06             1            1         0
            2010-03-05             1            1         0
            2010-03-04             1            1         0
            2010-03-03             1            1         0
            2010-03-02             1            1         0
            2010-03-01             1            1         0
            2010-02-28             1            1         0
            2010-02-27             1            1         0
            2010-02-26             1            1         0
            2010-02-25             1            1         0
            2010-02-24             1            1         0
            2010-02-23             1            1         0
            2010-02-22             1            1         0
            2010-02-21             1            1         0
            2010-02-20             1            1         0
            2010-02-19             1            1         0
            2010-02-18             1            1         0
            2010-02-17             1            1         0
            2010-02-16             1            1         0
            2010-02-15             1            1         1
            2010-02-14             0            0         0
            2010-02-13             0            0         0
            2010-02-12             0            0         0
            2010-02-11             0            0         0
            2010-02-10             0            0         0
            2010-02-09             0            0         0
            2010-02-08             0            0         0
            2010-02-07             0            0         0
            2010-02-06             0            0         0
            2010-02-05             0            0         0
            2010-02-04             0            0         0
            2010-02-03             0            0         0
            2010-02-02             0            0         0
            2010-02-01             0            0         0
            2010-01-31             0            0         0
            2010-01-30             0            0         0
            2010-01-29             0            0         0
            2010-01-28             0            0         0
            2010-01-27             0            0         0
            2010-01-26             0            0         0
            2010-01-25             0            0         0
        '''.split()

    def test_show_usage_monthly(self):
        out = StringIO()
        call_command('show_usage', '--monthly',
                     '--subscription-start={}'.format(
                         self.subscription_start.isoformat()),
                     '--after=6/8/2014',
                     '--before=12/25/2015',
                     stdout=out)
        assert out.getvalue().split() == '''
            month    start       end           registered    activated    active
            -------  ----------  ----------  ------------  -----------  --------
            Y06 M12  2015-12-24  2015-12-25             7            7         0
            Y06 M11  2015-11-24  2015-12-24             7            7         0
            Y06 M10  2015-10-24  2015-11-24             7            7         0
            Y06 M09  2015-09-24  2015-10-24             7            7         1
            Y06 M08  2015-08-24  2015-09-24             6            6         0
            Y06 M07  2015-07-24  2015-08-24             6            6         0
            Y06 M06  2015-06-24  2015-07-24             6            6         0
            Y06 M05  2015-05-24  2015-06-24             6            6         0
            Y06 M04  2015-04-24  2015-05-24             6            6         0
            Y06 M03  2015-03-24  2015-04-24             6            6         0
            Y06 M02  2015-02-24  2015-03-24             6            6         0
            Y06 M01  2015-01-24  2015-02-24             6            6         1
            Y05 M12  2014-12-24  2015-01-24             5            5         0
            Y05 M11  2014-11-24  2014-12-24             5            5         0
            Y05 M10  2014-10-24  2014-11-24             5            5         0
            Y05 M09  2014-09-24  2014-10-24             5            5         0
            Y05 M08  2014-08-24  2014-09-24             5            5         0
            Y05 M07  2014-07-24  2014-08-24             5            5         0
            Y05 M06  2014-06-24  2014-07-24             5            5         0
            Y05 M05  2014-05-24  2014-06-24             5            5         0
        '''.split()

    def test_show_usage_quarterly(self):
        out = StringIO()
        call_command('show_usage', '--quarterly',
                     '--subscription-start={:%m/%d/%Y}'.format(
                         self.subscription_start),
                     stdout=out)
        assert out.getvalue().split() == '''
            quarter    start       end           registered    activated    active
            ---------  ----------  ----------  ------------  -----------  --------
            Y08 Q1     2017-01-24  2017-04-04             9            9         1
            Y07 Q4     2016-10-24  2017-01-24             8            8         0
            Y07 Q3     2016-07-24  2016-10-24             8            8         0
            Y07 Q2     2016-04-24  2016-07-24             8            8         0
            Y07 Q1     2016-01-24  2016-04-24             8            8         1
            Y06 Q4     2015-10-24  2016-01-24             7            7         0
            Y06 Q3     2015-07-24  2015-10-24             7            7         1
            Y06 Q2     2015-04-24  2015-07-24             6            6         0
            Y06 Q1     2015-01-24  2015-04-24             6            6         1
            Y05 Q4     2014-10-24  2015-01-24             5            5         0
            Y05 Q3     2014-07-24  2014-10-24             5            5         0
            Y05 Q2     2014-04-24  2014-07-24             5            5         0
            Y05 Q1     2014-01-24  2014-04-24             5            5         1
            Y04 Q4     2013-10-24  2014-01-24             4            4         0
            Y04 Q3     2013-07-24  2013-10-24             4            4         0
            Y04 Q2     2013-04-24  2013-07-24             4            4         0
            Y04 Q1     2013-01-24  2013-04-24             4            4         1
            Y03 Q4     2012-10-24  2013-01-24             3            3         0
            Y03 Q3     2012-07-24  2012-10-24             3            3         0
            Y03 Q2     2012-04-24  2012-07-24             3            3         0
            Y03 Q1     2012-01-24  2012-04-24             3            3         1
            Y02 Q4     2011-10-24  2012-01-24             2            2         0
            Y02 Q3     2011-07-24  2011-10-24             2            2         0
            Y02 Q2     2011-04-24  2011-07-24             2            2         0
            Y02 Q1     2011-01-24  2011-04-24             2            2         1
            Y01 Q4     2010-10-24  2011-01-24             1            1         0
            Y01 Q3     2010-07-24  2010-10-24             1            1         0
            Y01 Q2     2010-04-24  2010-07-24             1            1         0
            Y01 Q1     2010-01-24  2010-04-24             1            1         1
        '''.split()

    def test_show_usage_yearly(self):
        out = StringIO()
        call_command('show_usage', '--yearly',
                     '--subscription-start={:%m/%d/%Y}'.format(
                         self.subscription_start),
                     '--ascending',
                     stdout=out)
        assert out.getvalue().split() == '''
            year    start       end           registered    activated    active
            ------  ----------  ----------  ------------  -----------  --------
            Y01     2010-01-24  2011-01-24             1            1         1
            Y02     2011-01-24  2012-01-24             2            2         1
            Y03     2012-01-24  2013-01-24             3            3         1
            Y04     2013-01-24  2014-01-24             4            4         1
            Y05     2014-01-24  2015-01-24             5            5         1
            Y06     2015-01-24  2016-01-24             7            7         2
            Y07     2016-01-24  2017-01-24             8            8         1
            Y08     2017-01-24  2017-04-04             9            9         1
        '''.split()
