import pandas as pd
from googleapiclient.discovery import build
from  modules.Credentials import check_credentials
from modules.GoogleSheets2 import rgb


class GSlide():

    def __init__(self, file_id):
        self.service = build('slides', 'v1', credentials=check_credentials())
        self.presentations = self.service.presentations()
        self.file_id = file_id


    def batch_update(self, requests):
        file_id = self.file_id
        body = {'requests': requests}
        return self.presentations.batchUpdate(presentationId=file_id, body=body).execute()


    def random_id(self, prefix):
        return Misc.random_string_and_numbers(6, prefix + "_")


    # Elements
    def element_create_image_request(self, page_id, image_url, x_pos=200, y_pos=200, width=100, height=100):
        return {  "createImage": {
                  "url"        : image_url,
                  "elementProperties": {
                      "pageObjectId": page_id,
                      "size": { "width" : { "magnitude": width, "unit": "PT" },
                                "height": { "magnitude": height,"unit": "PT" }},
                      "transform": { "scaleX": 1, "scaleY": 1, "translateX": x_pos, "translateY": y_pos, "unit": "PT" }}}}


    def element_create_image(self, page_id, image_url, x_pos=200, y_pos=200, width=100, height=100):
        requests = [ self.element_create_image_request(page_id, image_url, x_pos, y_pos, width, height)]
        result = self.batch_update(requests)
        return result.get('replies')[0].get('createImage').get('objectId')


    def element_create_table_request(self, slide_id, rows=3, cols=3, x_pos=200, y_pos=200, width=100, height=100, objectId=None):
        return { "createTable": { "objectId"         : objectId,
                                  "elementProperties": { "pageObjectId": slide_id,
                                                         "size"        : { "width": {"magnitude":  width, "unit": "PT"},
                                                                           "height": {"magnitude": height,"unit": "PT"}},
                                                         "transform"   : { "scaleX": 1, "scaleY": 1, "translateX": x_pos, "translateY": y_pos,"unit": "PT" }},
                                  "rows"             : rows                         ,
                                  "columns"          : cols                        }}
                                  #"tableRows"        : [{'rowHeight':{ 'magnitude': 10, 'unit': 'PT'}},{'rowHeight':{ 'magnitude': 100, 'unit': 'PT'}}]}}


    def element_create_table(self, slide_id, rows=3, cols=3, x_pos=200, y_pos=200, width=100, height=100, objectId=None):
        requests = [  self.element_create_table_request(slide_id, rows, cols, x_pos, y_pos, width, height, objectId) ]
        result = self.batch_update(requests)
        if result:
            return result.get('replies')[0].get('createTable').get('objectId')


    def element_create_shape_request(self, page_id, x_pos=200, y_pos=200, width=100, height=100, objectId=None):
        return { 'createShape': { 'objectId': objectId,
                                  'shapeType': 'TEXT_BOX',
                                  'elementProperties': {
                                      'pageObjectId': page_id,
                                      'size'        : { 'height': { 'magnitude': height, 'unit': 'PT'},
                                                        'width' : { 'magnitude': width , 'unit': 'PT'}},
                                      'transform'   : { 'scaleX': 1, 'scaleY': 1, 'translateX': x_pos, 'translateY': y_pos, 'unit': 'PT' }}}}


    def element_create_text_requests(self, page_id, text = "Text...", x_pos=200, y_pos=200, width=100, height=100, objectId=None):
        return [ self.element_create_shape_request(page_id, x_pos, y_pos, width, height, objectId),
                 self.element_insert_text_request(objectId,text)]


    def element_create_text(self, page_id, text = "Text...", x_pos=200, y_pos=200, width=100, height=100, objectId=None):
        requests = self.element_create_text_requests(page_id, text, x_pos, y_pos, width, height, objectId)
        result = self.batch_update(requests)
        if result:
            return result.get('replies')[0].get('createShape').get('objectId')


    def element_create_shape(self, page_id, shape_type, x_pos=200, y_pos=200, width=100, height=100):
        requests = [ { 'createShape': { 'shapeType': shape_type,
                                        'elementProperties': {
                                            'pageObjectId': page_id,
                                            'size'        : { 'height': { 'magnitude': height, 'unit': 'PT'},
                                                              'width' : { 'magnitude': width , 'unit': 'PT'}},
                                            'transform'   : { 'scaleX': 1, 'scaleY': 1, 'translateX': x_pos, 'translateY': y_pos, 'unit': 'PT' }}}}]

        result = self.batch_update(requests)
        if result:
            return result.get('replies')[0].get('createShape').get('objectId')


    def element_delete(self, element_id):
        requests = [ {  'deleteObject' : { 'objectId': element_id } } ]
        return self.batch_update(requests)


    def element_insert_text_request(self, objectId, text):
        return { 'insertText': { 'objectId': objectId, 'insertionIndex': 0, 'text': text }}


    def element_set_table_cell_size_bold_requests(self, table_id, row, col, size, bold):
        style = {"bold": bold, "fontSize": { "magnitude": size, "unit": "PT" }}
        fields = "bold,fontSize"
        return self.element_set_table_text_style_request(table_id, row, col, style, fields)


    def element_set_table_text_style_request(self, shape_id, row, col,style, fields):
        return {'updateTextStyle': { 'objectId'    : shape_id  ,
                                     "cellLocation": {"rowIndex": row, "columnIndex": col},
                                     'style'       : style     ,
                                     'fields'      : fields   }}


    def element_set_table_text_requests(self, table_id, row, col, text):
        return     [#{ "deleteText": {   "objectId"      : table_id,
                    #                    "cellLocation"  : {  "rowIndex": row, "columnIndex": col   },
                    #                    "textRange"     : {"type": "ALL"                         }}},
                    { "insertText": {   "objectId"      : table_id,
                                        "cellLocation"  : {  "rowIndex": row, "columnIndex": col   },
                                        "text"          : text,
                                        "insertionIndex": 0                                       }}]


    def element_set_table_text(self, table_id, row, col, text):
        requests = self.element_set_table_text_requests(table_id, row, col, text)
        self.batch_update(requests)


    def element_set_table_column_width_request(self, table_id, column_index, column_width):
        return { 'updateTableColumnProperties': { 'objectId': table_id, "columnIndices": [column_index],
                                                  "tableColumnProperties": { 'columnWidth': { "magnitude": column_width, "unit": "PT" } },
                                                  "fields": "columnWidth" } }


    def element_set_table_cell_aligment_request(self, table_id, row_index, column_index, row_span, column_span, alignment='MIDDLE'):
        return { "updateTableCellProperties": { "objectId": table_id,
                                                "tableRange": {
                                                    "location": { "rowIndex":  row_index,"columnIndex": column_index },
                                                                  "rowSpan": row_span, "columnSpan": column_span },
                                                "tableCellProperties": { "contentAlignment": alignment },
                                                "fields": "contentAlignment"}}


    def element_set_table_row_height_request(self, table_id, height):
        return  { "updateTableRowProperties": {   "objectId": table_id,
                                                  "rowIndices": 0,
                                                  "tableRowProperties": { "minRowHeight":  { 'magnitude': height, 'unit': 'PT'}},
                                                  "fields"            : "minRowHeight"}}


    def element_set_text_requests(self, element_id, text):
        return [ {   'deleteText' : { 'objectId'      : element_id         ,
                                      'textRange'     : { 'type': 'ALL' }}},
                 {
                     'insertText': { 'objectId'      : element_id          ,
                                     'insertionIndex': 0                   ,
                                     'text'          : text              }}]


    def element_set_text(self, element_id, text):
        requests =  self.element_set_text_requests(element_id, text)

        return self.batch_update(requests)


    def element_set_text_style_requests(self, object_id, style, fields):
        return {'updateTextStyle': { 'objectId': object_id  ,
                                     'style'   : style     ,
                                     'fields'  : fields   }}


    def element_set_text_style(self, shape_id,style, fields):
        requests = [ self.element_set_text_style_requests(shape_id, style, fields) ]
        return self.batch_update(requests)


    def element_set_text_style_requests__for_title(self, shape_id, font_size, color='gray0'):
        r, g, b = rgb(color)
        style = {  'bold'            : True,
                   'fontFamily'      : 'Avenir',
                   'fontSize'        : { 'magnitude' : font_size, 'unit': 'PT' },
                   'foregroundColor' : {'opaqueColor': {'rgbColor': {'blue': b, 'green': g, 'red': r}}}}
        fields   = 'bold,fontFamily,fontSize,foregroundColor'

        return self.element_set_text_style_requests(shape_id, style, fields)


    def element_set_shape_properties(self, shape_id,properties , fields=None):
        if fields is None:
            fields = ",".join(list(set(properties)))
        requests = [{'updateShapeProperties': { 'objectId'         : shape_id     ,
                                                'shapeProperties'  : properties   ,
                                                'fields'           : fields     }}]
        return self.batch_update(requests)


    def presentation_create(self, title):
        body = { 'title': title }
        presentation = self.presentations.create(body=body).execute()
        return presentation.get('presentationId')


    def presentation_metadata(self):
        file_id = self.file_id
        try:
            return self.presentations.get(presentationId = file_id).execute()
        except:
            return None


    def slide_delete_request(self, slide_id):
        return { "deleteObject": { "objectId" : slide_id}}


    def slide_delete(self, slide_id):
        requests =   [ self.slide_delete_request(slide_id) ]
        return self.batch_update(requests)


    def slide_copy(self, slide_id, new_slide_id, objects_ids = {}):
        requests =   [ { "duplicateObject": {
                                                "objectId" : slide_id,
                                                "objectIds": objects_ids}} ]
        requests[0]['duplicateObject']['objectIds'][slide_id] = new_slide_id
        return self.batch_update(requests)


    def slide_create_request(self, new_slide_id=None, layout='BLANK' , insert_at= None ):
        return { "createSlide": {       "objectId"      : new_slide_id,
                                        'insertionIndex': insert_at,
                                        'slideLayoutReference': { 'predefinedLayout': layout } }}


    def slide_create(self, insert_at=1, layout='TITLE', new_slide_id=None):
        requests =   [ self.slide_create_request(new_slide_id, layout, insert_at)]
        result = self.batch_update(requests)
        if result:
            return result.get('replies')[0].get('createSlide').get('objectId')


    def slide_move_to_pos_request(self, slide_id, pos):
        return [{ "updateSlidesPosition": { "slideObjectIds": [ slide_id],
                                            "insertionIndex": pos }}]


    def slide_move_to_pos(self, slide_id, pos):
        requests = self.slide_move_to_pos_request(slide_id, pos)
        return self.batch_update(requests)


    def slide_elements(self, page_number):
        slides = self.slides()
        page   = slides[page_number]
        if page:
            return page.get('pageElements')
        return []


    def slide_elements_via_id(self, slide_id):
        slides = self.slides_indexed_by_id()
        slide = slides.get(slide_id)
        if slide:
            return slide.get('pageElements')
        return []


    def slide_elements_via_id_indexed_by_id(self, slide_id):
        elements = {}
        for element in self.slide_elements_via_id(slide_id):
            elements[element.get('objectId')] = element
        return elements


    def slides(self):
        presentation = self.presentation_metadata()
        if presentation:
            return presentation.get('slides')
        return []


    def slides_indexed_by_id(self):
        presentation = self.presentation_metadata()
        slides = {}
        if presentation:
            if presentation.get('slides') is not None:
                for slide in presentation.get('slides'):
                    slides[slide.get('objectId')] = slide
        return slides


    def get_slides_ids(self):
        slides_meta = self.slides_indexed_by_id()
        return list(slides_meta.keys())


    ############################# TABLE METHODS: ####################################################################

    def add_slide_with_table_from_df(self, slide_id, title, data, title_size=26, title_color='gray0', headers_color='gray', cells_color=None, columns_widths=[], columns_to_merge=[]):

        # check if there already exist a slide with that id
        slides_ids = self.get_slides_ids()
        if slide_id in slides_ids:
            print("")
        else:

            title_id = '{0}_title'.format(slide_id)
            table_id = '{0}_table'.format(slide_id)

            headers = list(data.columns)
            rows = len(data) + 1
            cols = len(data.columns)

            if len(title) > 45:
                title_size -= 4

            requests = [self.slide_create_request(slide_id),
                        self.element_create_shape_request(slide_id, 10, 10, 500, 50, title_id),
                        self.element_insert_text_request(title_id, title),
                        self.element_set_text_style_requests__for_title(title_id, title_size, title_color),
                        self.element_create_table_request(slide_id, rows, cols, 12, 60, 700, 270, table_id)]

            for index, header in enumerate(headers):
                requests.extend(self.element_set_table_text_requests(table_id, 0, index, header))
                requests.append(self.element_set_table_cell_size_bold_requests(table_id, 0, index, 10, True))
                requests.append(self.element_set_table_row_height_request(table_id, 10))

                for i in range(len(data)):
                    cell_text = str(data[header][i])
                    s = 8

                    if len(cell_text) > 300:
                        s = 3
                    elif len(cell_text) > 200:
                        s = 4
                    elif len(cell_text) > 100: 
                        s = 5
                    elif len(cell_text) > 50:
                        s = 6
                    if len(cell_text) > 30:
                        s = 7

                    requests.extend(self.element_set_table_text_requests(table_id, i+1, index, cell_text))
                    if cell_text != '':
                        pass
                        requests.append(self.element_set_table_cell_size_bold_requests(table_id, i+1, index, s, False))

            self.batch_update(requests)

            # Color table headers
            self.set_multiple_cells_background_color(table_id, start_row=0, end_row=1, start_col=0, end_col=len(headers), color=headers_color)

            # Color table cells
            if cells_color is not None: 
                self.set_multiple_cells_background_color(table_id, start_row=1, end_row=rows, start_col=0, end_col=len(headers), color=cells_color)

            # Columns widths:
            if len(data.columns) == len(columns_widths):
                self.set_columns_widths(table_id, columns_widths)

            # Merge cells
            if len(columns_to_merge) != 0:
                self.merge_table(table_id, data, columns_to_merge)

            return table_id, title_id


    def cell_background_color_request(self, table_id, row, col, color):
        r, g, b = rgb(color)
        return {'updateTableCellProperties': 
                    { 'objectId': table_id,
                      'tableRange': {
                          'location': {
                              'rowIndex': row,
                              'columnIndex': col
                                       },
                          'rowSpan': 1,
                          'columnSpan': 1
                                    },
                      'tableCellProperties': {
                          'tableCellBackgroundFill': {
                              'solidFill': {
                                  'color': {
                                      'rgbColor': {
                                          'red': r,
                                          'green': g,
                                          'blue': b,
                                      }
                                  }
                              }
                          }
                      },
                      'fields': 'tableCellBackgroundFill'
                    }
               }


    def set_cell_background_color(self, table_id, row, col, color):
        requests = [self.cell_background_color_request(table_id, row, col, color)]
        self.batch_update(requests)


    def set_multiple_cells_background_color(self, table_id, start_row, end_row, start_col, end_col, color):
        requests = [self.cell_background_color_request(table_id, row, col, color) for row in range(start_row, end_row) for col in range(start_col, end_col)]
        self.batch_update(requests)


    def set_columns_widths(self, table_id, columns_widths):

        n = len(columns_widths)
        requests = []
        for i, w in zip(range(n), columns_widths):
            request = self.element_set_table_column_width_request(table_id, column_index=i, column_width=w)
            requests.append(request)

        if len(requests) > 0: self.batch_update(requests)


    def merge_table_cells_request(self, table_id, row_index, col_index, row_span, col_span=1):
        return {'mergeTableCells': {'objectId': table_id,
                                  'tableRange': {
                                      'location': {'rowIndex': row_index, 
                                                   'columnIndex': col_index},
                                      'rowSpan': row_span,
                                      'columnSpan': col_span
                                  }
                                 }}


    def merge_table_cells(self, table_id, row_index, col_index, row_span, col_span=1):
        request = self.merge_table_cells_request(table_id, row_index, col_index, row_span, col_span)
        self.batch_update(request)


    def merge_table(self, table_id, df, columns_to_merge):
        cols = {}
        col_names = df.columns.to_list()
        for name in columns_to_merge:
            if name in col_names:
                cols[name] = df.columns.get_loc(name) 

        for col in cols:
            values = df[col].unique() # unique values in col

            for value in values:
                c = df[col][df[col] == value].index.tolist()

                if len(c) > 1:
                    j = cols[col]
                    for i in c:
                        self.delete_table_cell_text(table_id, row=i+1, col=j)
                    self.element_set_table_text(table_id, row=c[0]+1, col=j, text=value)
                    self.merge_table_cells(table_id, row_index=c[0]+1, col_index=j, row_span=len(c))

        self.element_set_table_row_height(table_id, height=3)


    def element_set_table_row_height(self, table_id, height):
        request = self.element_set_table_row_height_request(table_id, height)
        self.batch_update(request)


    def delete_table_cell_text_request(self, table_id, row, col):
        return { "deleteText": {   "objectId"      : table_id,
                                        "cellLocation"  : { "rowIndex": row, "columnIndex": col   },
                                        "textRange"     : { "type": "ALL"                         }}}


    def delete_table_cell_text(self, table_id, row, col):
        request = self.delete_table_cell_text_request(table_id, row, col)
        self.batch_update(request)


    ############################# MASTER SLIDES METHODS: ####################################################################

    def slide_background_image_request(self, page_id, image_url):
         return {'updatePageProperties': {
                     'objectId': page_id,
                     'pageProperties': {
                     'pageBackgroundFill': {
                         'stretchedPictureFill': {
                             'contentUrl': image_url
                         }
                      }
                      },
                      'fields': 'pageBackgroundFill'
                  }}


    def set_slide_background_image(self, page_id, image_url):
        requests = [self.slide_background_image_request(page_id, image_url)]
        self.batch_update(requests)


    def slide_background_color_request(self, page_id, color):
        r, g, b = rgb(color)
        return {'updatePageProperties': {
                    'objectId': page_id,
                    'pageProperties': {
                        'pageBackgroundFill': {
                            'solidFill': {
                                'color': {
                                    'rgbColor': {
                                        'red': r,
                                        'green': g,
                                        'blue': b,
                                    }
                                }
                             }
                         }
                     },
                    'fields': 'pageBackgroundFill'
               }}


    def set_slide_background_color(self, page_id, color):
        requests = [self.slide_background_color_request(page_id, color)]
        self.batch_update(requests)

