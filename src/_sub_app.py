
import numpy as np
import pandas as pd

from ._app import Application
from ._constants import *
from ._log_utils import logger


class Courses(Application):
    """Class for the courses.
    """
    def __init__(self):
        super().__init__('courses_list')
        self.add_item()

    def add_item(self) -> None:
        """Adds a key (column) to the whitelist.
        """
        # The columns that will be added to the whitelist.
        items = [
            'name', 'description',
            'instructor', 'section', 'time',
            'days', 'location', 'credits',
        ]

        # The tests that will be added to the whitelist.
        for test in TESTS:
            if test == 'FE':
                items.append(test)
                continue

            # Differentiate the total marks and converted marks.
            test_total = f'{test}_total'
            test_convert = f'{test}_convert'

            # Add the items to the whitelist.
            items.append(test_total)
            items.append(test_convert)

        # Add the items to the whitelist.
        for item in items:
            super().add_item(item)

class Students(Application):
    """Class for the students.
    """
    def __init__(self):
        super().__init__('students_info')
        self.add_item()

    def add_item(self) -> None:
        """Adds a key (column) to the whitelist.
        """
        # The columns that will be added to the whitelist.
        items = [
            'name', 'id', 'email',
            'phone', 'address', 'city',
            'state', 'zip', 'country',
        ]

        # Add the items to the whitelist.
        for item in items:
            super().add_item(item)

class Results(Application):
    """Class for the student test results.
    """
    def __init__(self):
        super().__init__('results')

        # This class will be using the Courses and Students class.
        self._courses = Courses()
        self._students = Students()

        # Add the items to the whitelist.
        self.add_item()

        # Remove the items from the whitelist. This is to prevent the user from editing these items.
        self.remove_item(item='course_code')
        self.remove_item(item='student_code')

    @property
    def courses_db(self) -> pd.DataFrame:
        """Gets the courses database.
        """
        return self._courses.pull()

    @property
    def students_db(self) -> pd.DataFrame:
        """Gets the students database.
        """
        return self._students.pull()

    def add_item(self) -> None:
        """Adds a key (column) to the whitelist.
        """
        items = []
        items += TESTS

        # Add the items to the whitelist.
        for item in items:
            super().add_item(item)

    def view(self, student_code: str, course_code: str) -> pd.DataFrame:
        """Looks up the student's test results in a course.
        """
        df = self.pull()

        # Return a filtered dataframe.
        return df.loc[ (df['student_code'] == student_code) & (df['course_code'] == course_code) ]

    def append(self, student_code: str, course_code: str) -> None:
        """Appends a student into a course.
        """
        # Check if the student exists.
        if student_code not in self.students_db.index:
            return logger.bind(excluded=True).warning(f'{self.class_name}: Student not exists: {student_code}')
        # Check if the course exists.
        if course_code not in self.courses_db.index:
            return logger.bind(excluded=True).warning(f'{self.class_name}: Course not exists: {course_code}')

        df = self.pull()

        # If the database is empty, then bypass the checks.
        if df.empty:
            pass
        # Else if the course code is not in the database, then bypass the checks.
        elif course_code not in df['course_code'].tolist():
            pass
        # Else, check if the student is already in the course. If so, then return.
        elif student_code in df.loc[df['course_code'] == course_code]['student_code'].tolist():
            return logger.bind(excluded=True).warning(f'{self.class_name}: Student already exists: {student_code} in {course_code}')

        # Create a new entry by adding the children as keys and None as values.
        entry = {k: [None] for k in self.children}
        # Add the course code and student code.
        entry['course_code'] = [course_code]
        entry['student_code'] = [student_code]

        # Concatenate the new entry into the database.
        # In this class, the index won't be used. So, we will ignore the index.
        final = pd.concat(
            [df, pd.DataFrame(entry)],
            ignore_index=True,
            verify_integrity=True,
            sort=True
        )

        self.push(final)
        logger.info(f'{self.class_name}: {student_code} appended successfully into {course_code}.')

    def delete(self, student_code: str, course_code: str):
        """Deletes a student from a course.
        """
        df = self.pull()

        # If the database is empty, return.
        if df.empty:
            return logger.bind(excluded=True).warning(f'{self.class_name}: Database is empty.')
        # Else if the course code is not in the database, return.
        elif course_code not in df['course_code'].tolist():
            return logger.bind(excluded=True).warning(f'{self.class_name}: Course not exists: {course_code}')
        # Else, check if the student is not in the course. If so, then return.
        elif student_code not in df.loc[df['course_code'] == course_code]['student_code'].tolist():
            return logger.bind(excluded=True).warning(f'{self.class_name}: Student not exists: {student_code} in {course_code}')

        # Get the index of the entry.
        index = df[ (df['student_code'] == student_code) & (df['course_code'] == course_code) ].index
        # Delete the entry from the database.
        df.drop(index, inplace=True)

        self.push(df)
        logger.warning(f'{self.class_name}: Student: {student_code} in {course_code} deleted successfully.')

    def edit(self, student_code: str, course_code: str, **kwargs):
        """Edits a student's test results in a course.
        """
        df = self.pull()

        # If the database is empty, return.
        if df.empty:
            return logger.bind(excluded=True).warning(f'{self.class_name}: Database is empty.')
        # Else if the course code is not in the database, return.
        elif course_code not in df['course_code'].tolist():
            return logger.bind(excluded=True).warning(f'{self.class_name}: Course not exists: {course_code}')
        # Else, check if the student is not in the course. If so, then return.
        elif student_code not in df.loc[df['course_code'] == course_code]['student_code'].tolist():
            return logger.bind(excluded=True).warning(f'{self.class_name}: Student not exists: {student_code} in {course_code}')

        # Get the index of the entry.
        index = df[ (df['student_code'] == student_code) & (df['course_code'] == course_code) ].index

        # Go through the kwargs and edit the entry.
        for k, v in kwargs.items():
            # If the key is not in the whitelist, then return.
            if k not in self.children:
                return logger.bind(excluded=True).warning(f'{self.class_name}: Key not in whitelist: {k}')

            # Edit the entry with the new value.
            df.loc[index, k] = v

        self.push(df)
        logger.info(f'{self.class_name}: Student: {student_code} in {course_code} edited successfully.')

    def search(self, keyword: str) -> pd.DataFrame:
        """Searches for a student or a course.
        """
        df = self.pull()

        # If the keyword is similar to a course code, then return the filtered dataframe based on the course code.
        dfc = df[df['course_code'].str.contains(keyword, case=False)]

        # Return the filtered dataframe based on the course code if it is not empty.
        if not dfc.empty:
            return dfc

        # Else if the keyword is similar to a student code, then return the filtered dataframe based on the student code.
        dfs = df[df['student_code'].str.contains(keyword, case=False)]
        return dfs

class Assessments(Results):
    """TODO: Calculate the final marks of a student in a course.
    Calculates the mean, median, mode, and standard deviation of the test results.
    """
    def __init__(self):
        super().__init__()
        self.results = Results()

    def total(self):
        df=self.pull()
        rowlen=len(df.axes[0])
        counter=0
        ttllst=[]
        a1lst=[]
        a2lst=[]
        felst=[]
        t1lst=[]
        t2lst=[]

        while counter<rowlen:
            a1=df['A1'].iloc[counter]
            a1=int(a1)
            a2=df['A2'].iloc[counter]
            a2=int(a2)
            t1 = df['T1'].iloc[counter]
            t1=int(t1)
            t2 = df['T2'].iloc[counter]
            t2=int(t2)
            fe = df['FE'].iloc[counter]
            fe=int(fe)
            sum = a1 + a2 + t1 + t2 + fe

            a1lst.append(a1)
            a2lst.append(a2)
            t1lst.append(t1)
            t2lst.append(t2)
            felst.append(fe)
            ttllst.append(sum)
            counter=counter+1

        newcolumn=pd.DataFrame(df)
        newcolumn['Total Marks']=ttllst





        return(ttllst,a1lst,a2lst,t1lst,t2lst,felst,df)

    def ttlmean(self):
        ttltotal=self.total()[0]

        tttl=sum(ttltotal)
        ttlnum=len(ttltotal)
        mean=tttl/ttlnum

        return(mean)

    def a1mean(self):
        ttl=self.total()[1]
        tttl=sum(ttl)
        ttlnum=len(ttl)
        mean=tttl/ttlnum

        return(mean)

    def a2mean(self):
        ttl = self.total()[2]
        tttl = sum(ttl)
        ttlnum = len(ttl)
        mean = tttl / ttlnum

        return (mean)

    def t1mean(self):
        ttl = self.total()[3]
        tttl = sum(ttl)
        ttlnum = len(ttl)
        mean = tttl / ttlnum

        return (mean)

    def t2mean(self):
        ttl = self.total()[4]
        tttl = sum(ttl)
        ttlnum = len(ttl)
        mean = tttl / ttlnum

        return (mean)

    def femean(self):
        ttl = self.total()[5]
        ttl = sum(ttl)
        ttlnum = len(ttl)
        mean = ttl / ttlnum

        return (mean)

    def ttlmedian(self):
        ttltotal = self.total()[0]
        ttltotal.sort()
        median = len(ttltotal) // 2
        resultant = (ttltotal[median] + ttltotal[median]) / 2
        return(resultant)

    def a1median(self):
        ttltotal = self.total()[1]
        ttltotal.sort()
        median = len(ttltotal) // 2
        resultant = (ttltotal[median] + ttltotal[median]) / 2
        return(resultant)

    def a2median(self):
        ttltotal = self.total()[2]
        ttltotal.sort()
        median = len(ttltotal) // 2
        resultant = (ttltotal[median] + ttltotal[median]) / 2
        return(resultant)

    def t1median(self):
        ttltotal = self.total()[3]
        ttltotal.sort()
        median = len(ttltotal) // 2
        resultant = (ttltotal[median] + ttltotal[median]) / 2
        return(resultant)

    def t2median(self):
        ttltotal = self.total()[4]
        ttltotal.sort()
        median = len(ttltotal) // 2
        resultant = (ttltotal[median] + ttltotal[median]) / 2
        return(resultant)

    def femedian(self):
        ttltotal = self.total()[5]
        ttltotal.sort()
        median = len(ttltotal) // 2
        resultant = (ttltotal[median] + ttltotal[median]) / 2
        return(resultant)

    def ttlmax(self):
        ttltotal = self.total()[0]
        ttltotal.sort()
        resultant=ttltotal[0]
        return (resultant)

    def a1max(self):
        ttltotal = self.total()[1]
        ttltotal.sort()
        resultant = ttltotal[0]
        return (resultant)

    def a2max(self):
        ttltotal = self.total()[2]
        ttltotal.sort()
        resultant = ttltotal[0]
        return (resultant)

    def t1max(self):
        ttltotal = self.total()[3]
        ttltotal.sort()
        resultant = ttltotal[0]
        return (resultant)

    def t2max(self):
        ttltotal = self.total()[4]
        ttltotal.sort()
        resultant = ttltotal[0]
        return (resultant)

    def femax(self):
        ttltotal = self.total()[5]
        ttltotal.sort()
        resultant = ttltotal[0]
        return (resultant)

    def ttlmin(self):
        ttltotal = self.total()[0]
        ttltotal.sort()
        resultant = ttltotal[-1]
        return (resultant)

    def a1min(self):
        ttltotal = self.total()[1]
        ttltotal.sort()
        resultant = ttltotal[-1]
        return (resultant)

    def a2min(self):
        ttltotal = self.total()[2]
        ttltotal.sort()
        resultant = ttltotal[-1]
        return (resultant)

    def t1min(self):
        ttltotal = self.total()[3]
        ttltotal.sort()
        resultant = ttltotal[-1]
        return (resultant)

    def t2min(self):
        ttltotal = self.total()[4]
        ttltotal.sort()
        resultant = ttltotal[-1]
        return (resultant)

    def femin(self):
        ttltotal = self.total()[5]
        ttltotal.sort()
        resultant = ttltotal[-1]
        return (resultant)

    def ttlstd(self):
        ttltotal = self.total()[0]
        std=np.std(ttltotal)
        return(std)

    def a1std(self):
        ttltotal = self.total()[1]
        std = np.std(ttltotal)
        return (std)

    def a2std(self):
        ttltotal = self.total()[2]
        std = np.std(ttltotal)
        return (std)

    def t1std(self):
        ttltotal = self.total()[3]
        std = np.std(ttltotal)
        return (std)

    def t2std(self):
        ttltotal = self.total()[4]
        std = np.std(ttltotal)
        return (std)

    def festd(self):
        ttltotal = self.total()[5]
        std = np.std(ttltotal)
        return (std)

