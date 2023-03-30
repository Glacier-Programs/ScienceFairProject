from __future__ import annotations

class CSVFile:
    '''
    Constructors
    '''
    def __init__(self, headers: list[str], rows: list) -> None:
        # RAWDATA is straight from the file
        # no eddirting or processing beforehand
        self.headers = headers
        self.data = rows
    
    def from_file(RAWDATA: str) -> CSVFile:
        # RAWDATA is straight from the file
        # no eddirting or processing beforehand
        # gotta find lists 
        list_location_and_size = [] # (index, range)
        in_list = False
        this_list_index = 0
        this_list_length = 0
        for i, char in enumerate(RAWDATA):
            if not in_list and char == '"':
                in_list = True
                this_list_index = i
                this_list_length += 1

            elif in_list and char != '"':
                this_list_length += 1
            
            elif in_list and char ==  '"':
                this_list_length += 1
                in_list = False
                list_location_and_size.append( (this_list_index, this_list_length) )
                this_list_length = 0

        # replace the commas in each list with ps
        raw_as_list = list(RAWDATA)
        for location, length in [package for package in list_location_and_size]:
            list_data = RAWDATA[location:location+length]
            replaced_data = list_data.replace(',','.')
            raw_as_list[location:location+length] = replaced_data

        rows = ''.join(raw_as_list).split('\n')
        headers = rows[0].split(',')
        data = [row.split(',') for row in rows[1:]]
        return CSVFile(headers, data)
    
    def clone(self) -> CSVFile:
        return CSVFile( self.headers.copy(), self.data.copy() )

    '''
    Column / Row Option
    '''

    def get_column_index_by_header(self, header: str) -> int:
        index = 0
        current = ''
        while header != current:
            current = self.headers[index]
            index += 1
        # index will increment even after we found the right one
        return index - 1

    def get_column_by_header(self, header: str) -> list:
        index = self.get_column_index_by_header(header)
        values = []
        try:
            for row in self.data:
                values.append(row[index])
        except IndexError:
            return values
        return values
    
    def append_column(self, header: str, data: list) -> None:
        self.headers.append(header)
        for i, val in enumerate(data):
            self.data[i].append(val)
    
    def remove_column_by_header(self, header: str) -> list:
        # remove a column and return it
        return_column = []
        column_index = self.get_column_index_by_header(header)
        return_column.append( self.headers.pop(column_index))
        for row_number in range(len(self.data)):
            val = self.data[row_number].pop(column_index)
            return_column.append(val)
        return return_column

    def get_row(self, index: int) -> list:
        return self.data[index]
    
    def remove_row(self, index: int) -> list:
        return self.data.pop(index)
    
    def remove_rows(self, start: int, stop: int) -> None:
        for _ in range(start,stop):
            # since pop shortens list, the index will always be the same
            self.data.pop(start)

    '''
    Other Stuff
    '''

    def merge_file(self, other_file: CSVFile):
        # we want to merge the rows
        # so row 1 of the other file 
        # should be appended to row 
        # 1 of this file
        other_headers = other_file.headers
        other_rows = other_file.data
        self.headers.extend(other_headers)
        for i, row in enumerate(other_rows):
            self.data[i].extend(row)

    def reduce_to_last_column(self):
        last_column = self.get_column_by_header(self.headers[-1])
        self.data = self.data[:len(last_column)]

    def save_as(self, file_name: str) -> None:
        header_row = ','.join(self.headers)
        rows = []
        for r in self.data:
            as_line = ','.join([str(item) for item in r])
            rows.append(as_line)
        all_rows = '\n'.join(rows)
        full_file = header_row + '\n' + all_rows
        with open(file_name, 'w+') as file:
            file.write(full_file)

def clean_original_data(file_location_and_name: str):
    '''
    This does the things you needed:
    - Remove location, sunrise, sunset
    - put month and day into different column
    - create a line by combining multiple days
    '''
    with open(file_location_and_name, 'r') as file:
        CSV = CSVFile.from_file(file.read())

    # uncomment these lines when readjusting the original data
    # remove unnecessary column
    print(CSV.data[0])
    CSV.remove_column_by_header('stations')
    CSV.remove_column_by_header('preciptype')
    CSV.remove_column_by_header('description')
    print('0')
    CSV.remove_column_by_header('name')
    print('1')
    CSV.remove_column_by_header('sunrise')
    print('2')
    CSV.remove_column_by_header('sunset')
    print('3')
    CSV.remove_column_by_header('icon')
    print('5')
    CSV.remove_column_by_header('cloudcover')
    print('6')
    CSV.remove_column_by_header('conditions')
    print('7')

    # adjust month and day column
    date_time = CSV.remove_column_by_header('datetime') # year-month-day, method pops
    months = []
    days = []
    # year, month, day
    unformatted = [ entry.split('-') for entry in date_time[1:] ]
    for date in unformatted:
        months.append(date[1])
        days.append(date[2])
    # put them back into CSV
    CSV.append_column('month', months)
    CSV.append_column('day', days)

    # save file
    CSV.save_as("cleaned_data.csv")

def deep_clean_data(file_location_and_name: str):
    with open(file_location_and_name, 'r') as file:
        CSV = CSVFile.from_file(file.read())
    CSV.remove_column_by_header('snowdepth')
    CSV.remove_column_by_header('solarenergy')
    CSV.remove_column_by_header('solarradiation')
    CSV.remove_column_by_header('uvindex')
    CSV.remove_column_by_header('visibility')
    CSV.remove_column_by_header('dew')
    CSV.save_as('reduced.csv')

def create_multi_day_rows(file_location: str, days_merged: int) -> CSVFile:
    with open(file_location, 'r') as file:
        CSV = CSVFile.from_file(file.read())
    # need to create a new copy for each day being merged
    copies_of_main = []
    for i in range(1, days_merged):
        copy = CSV.clone()
        copy.remove_rows(0, i)
        # update the name of the headers
        for j in range(len(copy.headers)):
            copy.headers[j] += str(i)
        copies_of_main.append(copy)
    # merge all the clones
    main = copies_of_main[0]
    [main.merge_file(copies_of_main[csv]) for csv in range(1,len(copies_of_main))]
    # create the expected days column column
    average_temperature_column = CSV.get_column_by_header('temp')
    reduced_average_temp = average_temperature_column[days_merged-1:]
    main.append_column('expected', reduced_average_temp)
    main.reduce_to_last_column()
    return main

if __name__ == '__main__':
    # remove non numerical entries
    clean_original_data('data.csv')
    deep_clean_data('cleaned_data.csv')
    # create data that looks at previous 3, 5, 7 days
    create_multi_day_rows('cleaned_data.csv', 4).save_as("d3.csv")
    create_multi_day_rows('cleaned_data.csv', 6).save_as("d5.csv")
    create_multi_day_rows('cleaned_data.csv', 8).save_as("d7.csv")
    # create super clean data then data that is previous 3, 5, 7 days
    create_multi_day_rows('reduced.csv', 4).save_as("reduced_d3.csv")
    create_multi_day_rows('reduced.csv', 6).save_as("reduced_d5.csv")
    create_multi_day_rows('reduced.csv', 8).save_as("reduced_d7.csv")
