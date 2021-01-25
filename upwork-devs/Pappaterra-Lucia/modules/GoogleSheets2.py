import pandas as pd
import time
from googleapiclient.discovery import build
from  modules.Credentials import check_credentials


class GSheet():

    def __init__(self, file_id):
        self.service = build('sheets', 'v4', credentials=check_credentials())
        self.spreadsheets = self.service.spreadsheets()
        self.file_id = file_id


    def sheets_metadata(self):
        file_id = self.file_id
        return self.spreadsheets.get(spreadsheetId=file_id).execute()


    def batch_update(self, requests):
        file_id = self.file_id
        body = {'requests': requests}
        return self.spreadsheets.batchUpdate(spreadsheetId=file_id, body=body).execute()


    def sheets_delete_sheet(self, sheet_id):
        request = { "deleteSheet": { "sheetId": sheet_id } }
        return self.batch_update([request])


    def sheets_add_sheet(self, sheet_name):
        request = { "addSheet": { "properties": { "title": sheet_name } } }
        result  =  self.batch_update([request])
        return result.get('replies')[0].get('addSheet').get('properties').get('sheetId')


    def df_to_googlesheet(self, df, sheet_name, ran='!A1', input_option='RAW'): 
        """
        Exports pandas dataframe to google sheet.

        :param df: pandas dataframe with the data to be exported
        :param sheet_name: sheet name, if no sheet with that name, a new one is created
        :param ran: range, starting column
        :param input_option: if equal to 'RAW' the input is not parsed and is simply inserted as a string,
        if it is equal to 'USER_ENTERED' the input is parsed exactly as if it were entered into the Google Sheets UI, 
        so 'Mar 1 2016' becomes a date, and '=1+2' becomes a formula
        """
        file_id = self.file_id
        sheet_names = self.get_sheet_names()

        # If no sheet with that name, create new sheet
        if sheet_name not in sheet_names: 
            self.sheets_add_sheet(file_id, sheet_name)

        request = self.spreadsheets.values().update(
            spreadsheetId = file_id,
            valueInputOption = input_option,
            range = sheet_name + ran,
            body = dict(
                majorDimension = 'ROWS',
                values = df.T.reset_index().T.values.tolist()))
        output = request.execute()
    
        if len(df)*len(df.columns) > 100: time.sleep(25)


    def read_from_sheet(self, sheet_name, ran='!A:K'):
        """
        
        :param sheet_name:
        :param ran:
        :return: 
        """
        file_id = self.file_id
                      
        fields = 'sheets(data(rowData(values(note,userEnteredValue))))'
                      
        request = self.spreadsheets.get(
            spreadsheetId = file_id, 
            ranges = sheet_name + ran, 
            fields = fields)
                      
        output = request.execute() # this is a json
        
        # now convert it to df
        m = len(output['sheets'][0]['data'][0]['rowData'])
        col_len = 1

        rows = []
        for k in range(m):
            row = []
            
            values = output['sheets'][0]['data'][0]['rowData'][k]
            
            if values != {}:
                for elem in values['values']:
                    if elem != {}:
                        d = elem['userEnteredValue']
                        key = list(d.keys())[0]
                        row.append(d[key])
                    else:
                        row.append('')
            else:
                row.append('')
            
            if len(row) > col_len: 
                col_len = len(row)
            else:
                while len(row) != col_len: row.append('')

            rows.append(row)

        for elem in rows: 
            if len(elem) != col_len: rows.remove(elem)

        return pd.DataFrame(rows, columns=rows[0]).drop(0).reset_index(drop=True)


    def read_from_sheet2(self, sheet_name, ran='!A:K'):
        """
        
        :param sheet_name:
        :param ran:
        :return: 
        """
        file_id = self.file_id

        request = self.spreadsheets.values().get(
            spreadsheetId = file_id, 
            range = sheet_name + ran)

        result = request.execute() # this is a json
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            data = result.get('values') # it is like a json file
            print("COMPLETE: Data copied")

            # convert it to a pandas DataFrame
            df = pd.DataFrame(data, columns=data[1])

            return df.reset_index(drop=True)


    def get_sheet_names(self):
        """
        Create a list with current sheet names.
        
        :return: list with current sheet names
        """
        current_sheet_names = []
        for sheet in self.sheets_metadata()['sheets']:
            current_sheet_names.append(sheet['properties']['title'])
        
        return current_sheet_names
    
    
    def clear_sheet(self, sheet_id, start_row=0, end_row=100, start_col=0, end_col=20, time_sleep=0):
        """
        Clear all sheet cells and unmerge them given its id. Also delete all existing charts in sheet.
        
        :param sheet_id: sheet id
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1
        :param time_sleep: wait time before batch update
        """
        
        clear_request = [{"updateCells": {
                              "range": {
                                  "sheetId": sheet_id,
                                  "startRowIndex": start_row,
                                  "endRowIndex": end_row,
                                  "startColumnIndex": start_col,
                                  "endColumnIndex": end_col},
                                  "fields": "*"
                        }}]
    
        
        clear_filters_request = [{"clearBasicFilter": {
                                      "sheetId": sheet_id
                                 }
                            }]

        if time_sleep != 0: time.sleep(time_sleep)
            
        self.batch_update([clear_request, clear_filters_request])
        
        self.unmerge_cells(sheet_id, start_row, end_row, start_col, end_col, time_sleep)
        
        # Also delete all existing charts
        #self.delete_all_charts_in_sheet(sheet_id)
    
        self.set_column_width(sheet_id, 100, start_col, end_col) # default width is 100
        self.set_row_height(sheet_id, 21, start_row, end_row) # default height is 21
        
    
    def autofit_col(self, sheet_id, start_col=0, end_col=20, time_sleep=0):
        """
        Resize column to fit to data.
        
        :param sheet_id: sheet id
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1
        :param time_sleep: wait time before batch update
        """
        
        request = [{"autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": start_col,
                            "endIndex": end_col
                        }
                  }}]

        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
    
    
    def autofit_row(self, sheet_id, start_row=0, end_row=100, time_sleep=0):
        """
        Resize row to fit to data.
        
        :param sheet_id: sheet id
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param time_sleep: wait time before batch update
        """
        
        request = [{"autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": start_row,
                            "endIndex": end_row
                        }
                  }}]

        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
        

    def set_column_width(self, sheet_id, width, start_col, end_col, time_sleep=0):
        """
        Set column width.
        
        :param sheet_id: sheet id
        :param width: wanted column width
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1
        :param time_sleep: wait time before batch update
        """
        
        request = [{"updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": start_col,
                            "endIndex": end_col},
                        "properties": {
                            "pixelSize": width
                        },
                        "fields": "pixelSize"
                   }}]

        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)


    def set_row_height(self, sheet_id, height, start_row=0, end_row=100, time_sleep=0):
        """
        Set row height.
        
        :param sheet_id: sheet id
        :param height: wanted row height
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param time_sleep: wait time before batch update
        """
        
        request = [{"updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": start_row,
                            "endIndex": end_row
                        },
                        "properties": {
                            "pixelSize": height
                        },
                        "fields": "pixelSize"
                  }}]

        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
        

    def slow_update(self, requests, time_sleep=50):
        """
        Update google sheet file with given list of requested changes.
        
        :param requests: list of update requests
        :param time_sleep: wait time before batch update
        """
        l = len(requests)
        if l != 0: 
            if l < 100:
                self.batch_update(requests)
            else:
                for requests_chunk in create_chunks(requests, 99):
                    self.batch_update(requests_chunk)
                    time.sleep(time_sleep)


    def merge_cells_request(self, sheet_id, start_row, end_row, start_col, end_col):
        """
        Returns request to merge cells.
        
        :param sheet_id: sheet id
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1
        :return: a list with one request in json (or dict) format
        """
        request = [{"mergeCells": { 
                        "range": { 
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col
                        },
                        "mergeType": "MERGE_ALL"
                  }}]
        
        return request
        

    def merge_cells(self, sheet_id, df, cols, ref_cols=[], time_sleep=50):
        """
        Merge equal consecutive cells for all columns in cols. Columns can also be merged according to repeated values in other column.
        
        :param sheet_id: sheet id 
        :param df: pandas dataframe with the information that was previously exported to the google sheet
        :param cols: a dict with column names as key and their position in df as value, these are the columns that will be merged
        :param ref_cols: a list with the names of the columns that must be used as reference to merge the columns in cols. If no list is provided a list with the keys in cols will be used, that is, each column will be merged according to its own repeated values only
        :param time_sleep: wait time before batch update
        """
        
        requests = []
        
        if ref_cols == []: ref_cols = list(cols.keys())
        
        for col, ref_col in zip(cols, ref_cols):    
            values = df[ref_col].unique() # unique values in the reference column
            for value in values:
                c = df.index[df[ref_col] == value].tolist()    
                for cc in split_non_consecutive(c):
                    if len(cc) > 1:
                        request = self.merge_cells_request(sheet_id, start_row=cc[0]+1, end_row=cc[len(cc)-1]+2, start_col=cols[col], end_col=cols[col]+1)
                        requests.append(request)
                
        self.slow_update(requests, time_sleep)

        
    def unmerge_cells_request(self, sheet_id, start_row, end_row, start_col, end_col):
        """
        Returns request to unmerge cells.
        
        :param sheet_id: sheet id
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1
        """   
        unmerge_request = [{"unmergeCells": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "startRowIndex": start_row,
                                    "endRowIndex": end_row,
                                    "startColumnIndex": start_col,
                                    "endColumnIndex": end_col
                                }
                           }}]
        
        return unmerge_request
        
        
    def unmerge_cells(self, sheet_id, start_row=0, end_row=100, start_col=0, end_col=20, time_sleep=0):
        """
        Unmerge cells in the given range.
        
        :param sheet_id: sheet id
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1
        :param time_sleep: wait time before batch update
        """        
        
        unmerge_request = self.unmerge_cells_request(sheet_id, start_row, end_row, start_col, end_col)
        
        if time_sleep != 0: time.sleep(time_sleep)
            
        self.batch_update([unmerge_request])


    def request_cell_set_background_color(self, sheet_id, col, row, red, green, blue):
        return {'updateCells': { 'start': {'sheetId': sheet_id, 'rowIndex': row, 'columnIndex': col },
                                 'rows': [{'values': [ {'userEnteredFormat' : {'backgroundColor': {'red': red, 'blue': blue, 'green': green}}}] } ],
                                 'fields': 'userEnteredFormat.backgroundColor'}}


    def color_cells_request(self, sheet_id, indexes, color='white'):
        """
        Returns requests to fill cells with colors.
        
        :param sheet_id: sheet id
        :param indexes: a list of tuples (row, col) with the row and column indexes of the cells to be colored
        :param color: fill color
        :return: a list with all the color cells requests
        """
        requests = []
    
        r, g, b = rgb(color)

        for ind in indexes:
            requests.append(self.request_cell_set_background_color(sheet_id=sheet_id, col=ind[1], row=ind[0], red=r, green=g, blue=b))
    
        return requests


    def get_sheets_ids(self):
        """
        Returns a list with current sheet ids.
        
        :return: list with current sheet ids
        """   
        ss = self.sheets_metadata()['sheets']
        sheets_ids = []
        for i in range(len(ss)):
            sheets_ids.append(ss[i]['properties']['sheetId'])
    
        return sheets_ids


    def get_sheet_id(self, sheet_name):
        """
        Return sheet id given its name.
        
        :param sheet_name: sheet name
        :return: sheet id
        """
        ss = self.sheets_metadata()['sheets']
    
        for i in range(len(ss)):
            r = 0
            if ss[i]['properties']['title'] == sheet_name:
                r=+1
                return ss[i]['properties']['sheetId']
        if r==0:
            print("No sheet with that name.")
            return r 
    
    
    def get_sheets_names(self):
        """
        Returns a list with current sheet names.
        
        :return: list with current sheet names
        """   
        ss = self.sheets_metadata()['sheets']
        sheets_names = []
        for i in range(len(ss)):
            sheets_names.append(ss[i]['properties']['title'])
    
        return sheets_names
    
    
    def get_sheet_name(self, sheet_id):
        """
        Return sheet name given its id.
        
        :param sheet_id: sheet id
        :return: sheet name
        """
        ss = self.sheets_metadata()['sheets']
    
        name = ''
        for i in range(len(ss)):
            if ss[i]['properties']['sheetId'] == sheet_id:
                name = ss[i]['properties']['title']
        if name == '':
            print("No sheet with that id.")
 
        return name 


    def delete_sheet_by_id(self, sheet_id):
        """
        Delete file given its id.
        
        :param sheet_id: sheet id
        """
        sheets_ids = self.get_sheets_ids()
        
        if sheet_id in sheets_ids:
            self.sheets_delete_sheet(sheet_id)
        else:
            print("No sheet with that id.")
    
    
    def delete_sheet_by_name(self, sheet_name):
        """
        Delete sheet given its name.
        Note that there may be more than one sheet with that name in the file, 
        in which case it will delete the first one it finds.
        
        :param sheet_name: sheet name
        """
        sheets_names = self.get_sheets_names()
        
        if sheet_name in sheets_names:
            sheet_id = self.get_sheet_id(sheet_name)
            self.sheets_delete_sheet(sheet_id)
        else:
            print("No sheet with that name.")
    
    
    def set_headers(self, sheet_id, end_column, start_column=0, end_row=1, start_row=0, color='pale-blue', time_sleep=0):
        """
        Set fixed headers in bold, with background color.
        
        :param sheet_id: sheet id
        :param end_col: final column plus 1 
        :param start_col: starting column, first column is 0
        :param color: headers color
        :param time_sleep: wait time before batch update
        """
        r, g, b = rgb(color)
    
        requests =  [{"repeatCell": {
                          "range": { 
                              "sheetId": sheet_id,
                              "startRowIndex": start_row,
                              "endRowIndex": end_row,
                              "startColumnIndex": start_column,           
                              "endColumnIndex": end_column
                          },
                          "cell": {
                              "userEnteredFormat": {
                                  "backgroundColor": {
                                      "red": r, 
                                      "green": g, 
                                      "blue": b
                                  },
                                  "horizontalAlignment" : "CENTER",
                                  "textFormat": {
                                      "foregroundColor": {
                                          "red": 0.0, 
                                          "green": 0.0, 
                                          "blue": 0.0
                                      },
                                      "fontSize": 12,
                                      "bold": True 
                                  }
                              }
                          },
                          "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                     }
                     },
                     {"updateSheetProperties": {
                         "properties": {
                             "sheetId": sheet_id,
                             "gridProperties": {
                                 "frozenRowCount": 1
                             }
                                                               
                         },
                         "fields": "gridProperties.frozenRowCount"
                     }}]
        
        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(requests)
        
        
    def create_filter(self, sheet_id, start_col, end_col, start_row=0, end_row=1000, time_sleep=0):
        """
        Create a filter.
        
        :param sheet_id: sheet id
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1 
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param time_sleep: wait time before batch update
        """
        
        filterSettings = {"range": {
                              "sheetId": sheet_id,
                              "startRowIndex": start_row,
                              "endRowIndex": end_row,
                              "startColumnIndex": start_col,
                              "endColumnIndex": end_col
                              }
                         }
       
        
        request = [{"setBasicFilter": {
                        "filter": filterSettings }
                   }]

        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
        
        
    def make_bold(self, sheet_id, start_row, end_row, start_col, end_col, time_sleep=0):
        """
        Make bold the content in the given range.
        
        :param sheet_id: sheet id
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1
        :param time_sleep: wait time before batch update
        """
        
        request = [{"repeatCell": {
                        "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row + 1,
                        "endRowIndex": end_row + 1,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col
                        },
                        "cell": { "userEnteredFormat": {
                                      "textFormat": {
                                          "bold": True
                                        }
                                     }
                         },
                        "fields": "userEnteredFormat.textFormat.bold",
                       }
                    }]
        
        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
    
    
    def add_bottom_borders(self, sheet_id, start_row, end_row, start_col, end_col, width=2, style="SOLID", time_sleep=0):
        """
        Add border to cell bottom.
        
        :param sheet_id: sheet id
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1 
        :param width: border width
        :param style: border style
        :param time_sleep: wait time before batch update
        """
        
        request = [{"updateBorders": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col},
                        "bottom": {
                            "style": style,
                            "width": width,
                        },
                        "innerHorizontal": {
                            "style": style,
                            "width": width,
                        }
                   }}]

        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
    
    
    def add_vertical_borders(self, sheet_id, start_row, end_row, start_col, end_col, width=1, style="SOLID", time_sleep=0):
        """
        Add border to the right (or left) of cell.
        
        :param sheet_id: sheet id
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1 
        :param width: border width
        :param style: border style
        :param time_sleep: wait time before batch update
        """               
        
        request = [{"updateBorders": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col
                        },
                        "left": {
                            "style": style,
                            "width": width,
                        },
                        "innerVertical": {
                            "style": style,
                            "width": width,
                        }
                   }}]
        
        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
    

    def set_alignment(self, sheet_id, start_row=0, end_row=100, start_col=0, end_col=20, h_align="LEFT", v_align="MIDDLE", wrap="WRAP", time_sleep=0):
        """
        Align cell content.
        
        :param sheet_id: sheet id
        :param start_row: starting row, first row is 0
        :param end_row: final row plus 1
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1 
        :param h_align: horizontal alignment
        :param v_align: vertical alignment
        :param time_sleep: wait time before batch update
        """
        
        request = [{"repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col
                        },  
                        "cell": {
                            "userEnteredFormat": {
                                "horizontalAlignment": h_align,
                                "verticalAlignment": v_align,
                                "wrapStrategy": wrap
                            }
                        },
                        "fields": "userEnteredFormat",
                   }}]
        
        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
        
        
    def set_currency(self, sheet_id, start_col, end_col, currency='British Pound Sterling', time_sleep=0):
        """
        Format cell content to use a currency.
        
        :param sheet_id: sheet id
        :param start_col: starting column, first column is 0
        :param end_col: final column plus 1 
        :param currency: currency type
        :param time_sleep: wait time before batch update
        """
        
        if currency == 'British Pound Sterling':
            pattern = "\"£\"#,##0.00"
        elif currency == 'US Dolar':
            pattern = "\"$\"#,##0.00"            
        
        request = [{"repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat": {
                                    "type": "CURRENCY",
                                    "pattern": pattern
                                }
                            }
                        },
                        "fields": "userEnteredFormat.numberFormat"
                    }}]       
        
        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
        
        
    def add_bar_chart(self,
                      sheet_id, 
                      source_sheet_id=None,
                      title='',
                      domain_col=0,
                      domain_start_row=0,
                      series_col=1,
                      series_start_row=0,
                      end_row=100,
                      anchor_row=0, 
                      anchor_col=0,
                      chart_type="BAR",
                      time_sleep=0):
        """
        Plot a bar chart in sheet.
        
        :param sheet_id: sheet id of the sheet where the chart will be added
        :param source_sheet_id: sheet id of the sheet with the source information to be used for the chart
        :param title: string with chart title
        :param domain_col: column index of the domain to use as labels
        :param domain_start_row: domain starting row
        :param series_col: column index of the series to be plotted
        :param series_start_row: series starting row
        :param end_row: domain and series end row
        :param anchor_row: anchor row
        :param anchor_col: anchor column
        :param chart_type: chart type, can be "BAR" or "COLUMN"
        :param time_sleep: wait time before batch update
        """
        
        domain_start_col = domain_col
        domain_end_col = domain_col +1
        domain_end_row = end_row
        series_start_col = series_col
        series_end_col = series_col + 1
        series_end_row = end_row
        
        
        if source_sheet_id == None: source_sheet_id = sheet_id
            
        if chart_type == "BAR":
            target_axis = "BOTTOM_AXIS"
        elif chart_type == "COLUMN":
            target_axis = "LEFT_AXIS"
        
        request = [{"addChart": {
                        "chart": {
                            "spec": {
                                "title": title,
                                "basicChart": {
                                    "chartType": chart_type,
                                    "domains": [{"domain": {
                                                 "sourceRange": {
                                                     "sources": [{"sheetId": source_sheet_id,
                                                                  "startRowIndex": domain_start_row,
                                                                  "endRowIndex": domain_end_row,
                                                                  "startColumnIndex": domain_start_col,
                                                                  "endColumnIndex": domain_end_col
                                                                 }]
                                                 }                                                
                                               }}],
                                    "series": [{"series": {
                                                    "sourceRange": {
                                                    "sources": [{"sheetId": source_sheet_id,
                                                                 "startRowIndex": series_start_row,
                                                                 "endRowIndex": series_end_row,
                                                                 "startColumnIndex": series_start_col,
                                                                 "endColumnIndex": series_end_col
                                                                }]
                                                    }
                                               },
                                                "targetAxis": target_axis
                                               }],
                                    "headerCount": 1
                                }
                            },
                            "position": {
                                "overlayPosition": {
                                    "anchorCell": {
                                        "sheetId": sheet_id,
                                        "rowIndex": anchor_row,
                                        "columnIndex": anchor_col
                                    },
                                    "offsetXPixels": 50,
                                    "offsetYPixels": 50
                                }
                            }
                        }}}]
        
        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
        

    def add_pie_chart(self, 
                      sheet_id, 
                      source_sheet_id=None,
                      title='', 
                      domain_col=1,
                      domain_start_row=1,
                      series_col=0,
                      series_start_row=1,
                      end_row=100,    
                      anchor_row=0, 
                      anchor_col=0,
                      time_sleep=0):
        """
        Plot a pie chart in sheet.
        
        :param sheet_id: sheet id of the sheet where the chart will be added
        :param source_sheet_id: sheet id of the sheet with the source information to be used for the chart
        :param title: string with chart title
        :param domain_col: column index of the domain to use as labels
        :param domain_start_row: domain starting row
        :param series_col: column index of the series to be plotted
        :param series_start_row: series starting row
        :param end_row: domain and series end row
        :param anchor_row: anchor row
        :param anchor_col: anchor column
        :param time_sleep: wait time before batch update
        """
        
        domain_start_col = domain_col
        domain_end_col = domain_col +1
        domain_end_row = end_row
        series_start_col = series_col
        series_end_col = series_col + 1
        series_end_row = end_row
        
        if source_sheet_id == None: source_sheet_id = sheet_id
        
        request = [{"addChart": {
                        "chart": {
                            "spec": {
                                "title": title,
                                "pieChart": {
                                    "legendPosition": "RIGHT_LEGEND",
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [{"sheetId": source_sheet_id,
                                                         "startRowIndex": domain_start_row,
                                                         "endRowIndex": domain_end_row,
                                                         "startColumnIndex": domain_start_col,
                                                         "endColumnIndex": domain_end_col
                                                        }]
                                        }
                                    },
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{"sheetId": source_sheet_id,
                                                         "startRowIndex": series_start_row,
                                                         "endRowIndex": series_end_row,
                                                         "startColumnIndex": series_start_col,
                                                         "endColumnIndex": series_end_col
                                                        }]
                                        }
                                    },
                                }
                            },
                            "position": {
                                "overlayPosition": {
                                    "anchorCell": {
                                        "sheetId": sheet_id,
                                        "rowIndex": anchor_row,
                                        "columnIndex": anchor_col
                                    },
                                    "offsetXPixels": 50,
                                    "offsetYPixels": 50
                                }
                            }
                        }
                   }}]

        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)


    def get_chart_id(self, chart_title, chart_type='basicChart'):
        """
        Get chart id of specific chart.
        Note that if there are more than one chart of the same type with the same title,
        it will return the id of the one that finds first.
    
        :param chart_title: chart title
        :param chart_type: chart type, which can be 'basicChart' or 'pieChart'
        :return: chart id
        """
    
        for elem in self.sheets_metadata()['sheets']:
            if 'charts' in list(elem.keys()):   
                for elem2 in elem['charts']:
                    if elem2['spec']['title'] == chart_title and chart_type in list(elem2['spec'].keys()):
                        chart_id = elem2['chartId'] 

        return chart_id


    def get_charts_ids(self):
        """
        Returns a list with the ids of all charts in file.
        
        :return: list of charts ids
        """
        charts_ids = []
    
        for elem in self.sheets_metadata()['sheets']:
            if 'charts' in list(elem.keys()): 
                for elem2 in elem['charts']:
                    charts_ids.append(elem2['chartId'])

        return charts_ids


    def get_charts_ids_in_sheet(self, sheet_id):
        """
        Returns a list with the ids of all charts in sheet.
        
        :param sheet_id: sheet id
        :return: list of charts ids
        """
        charts_ids = []
    
        for elem in self.sheets_metadata()['sheets']:
            if elem['properties']['sheetId'] == sheet_id:
                if 'charts' in list(elem.keys()): 
                    for elem2 in elem['charts']:
                        charts_ids.append(elem2['chartId'])
                    
        return charts_ids

                
    def delete_chart(self, chart_id, time_sleep=0):
        """
        Delete chart given its id.
        
        :param chart_id: chart id
        :param time_sleep: wait time before batch update
        """
    
        request = [{"deleteEmbeddedObject": {
                        "objectId": chart_id
                    }}]

        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
    
    
    def delete_all_charts_in_file(self):
        """
        Delete all charts in file.
        """
        charts_ids = self.get_charts_ids()
    
        for chart_id in charts_ids:
            self.delete_chart(chart_id)
        
        
    def delete_all_charts_in_sheet(self, sheet_id):
        """
        Delet all charts in sheet.
        
        :param sheet_id: sheet id
        """
        charts_ids = self.get_charts_ids_in_sheet(sheet_id)
    
        for chart_id in charts_ids:
            self.delete_chart(chart_id)
        
                
    def resize_chart(self, chart_id, width, height, anchor_row=0, anchor_col=0, time_sleep=0):
        """
        Resize chart, anchor point (row, col) must be specified.
    
        :param chart_id: chart id
        :param width: wanted width
        :param height: wanted height
        :param anchor_row: anchor row
        :param anchor_col: anchor column
        :param time_sleep: wait time before batch update
        """
    
        request = [{"updateEmbeddedObjectPosition": {
                        "objectId": chart_id,
                        "newPosition": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "rowIndex": anchor_row,
                                    "columnIndex": anchor_col
                                },
                                "offsetXPixels": 100,
                                "widthPixels": width,
                                "heightPixels": height
                            }
                        },
                    "fields": "anchorCell(rowIndex,columnIndex),offsetXPixels,widthPixels,heightPixels"
                   }}]

        if time_sleep != 0: time.sleep(time_sleep)
        self.batch_update(request)
        
        
##################### Auxiliar functions ##############################################
  
    
def wrap_by_word(s, n):
    """
    Returns a string where \n is inserted between every n words.
    
    :param s: string
    :param n: integer, number of words
    :return: a string where \n is inserted between every n words
    """
    a = s.split()
    ret = ''
    for i in range(0, len(a), n):
        ret += ' '.join(a[i:i+n]) + '\n'
    return ret


def split_non_consecutive(data):
    """
    Split a list in sub-lists of consecutive elements.
    
    :param data: list
    :yield: lists of consecutive elements
    """
    data = iter(data)
    val = next(data)
    chunk = []
    try:
        while True:
            chunk.append(val)
            val = next(data)
            if val != chunk[-1] + 1:
                yield chunk
                chunk = []
    except StopIteration:
        if chunk:
            yield chunk
            
            
def create_chunks(list_name, n):
    """
    Yields successive 'n' sized chunks from list 'list_name'.
    
    :param list_name: list
    :param n: size of chunks
    :yield: successive 'n' sized chunks from list 'list_name'
    """
    for i in range(0, len(list_name), n):
        yield list_name[i:i + n]

            
def rgb(color='white'):
    """
    Given color name, returns its RGB values.
    
    :param color: string with color name
    :return: r, g, b values
    """
    r, g, b = 1, 1, 1
    
    if color == 'red':
        r, g, b = 1, 0, 0    
    elif color == 'green':
        r, g, b = 0, 1, 0 
    elif color == 'blue':
        r, g, b = 0, 0, 1
    elif color == 'green0':
        r, g, b = 0.6, 0.8, 0.3
    elif color == 'green1':
        r, g, b = 0, 0.4, 0.4
    elif color == 'blue0':
        r, g, b = 0.1, 0.6, 0.8
    elif color == 'blue1':
        r, g, b = 0.1, 0.4, 0.5
    elif color == 'light-blue':
        r, g, b = 0.2, 0.71, 1
    elif color == 'pale-blue':
        r, g, b = 0.85, 0.95, 0.96
    elif color == 'yellow':
        r, g, b = 1, 1, 0  
    elif color == 'gray':
        r, g, b = 0.85, 0.85, 0.85
    elif color == 'dark':
        r, g, b = 0.35, 0.35, 0.35
    elif color == 'violet':
        r, g, b = 0.8, 0.2, 0.6
    elif color == 'purple':
        r, g, b = 0.76, 0.48, 0.63
        
    return r, g, b

