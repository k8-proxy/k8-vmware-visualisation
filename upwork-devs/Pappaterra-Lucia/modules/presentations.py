from modules.GoogleDrive2 import GDrive
from modules.GoogleSheets2 import GSheet
from modules.GoogleSlides2 import GSlide


folder_id = '1dELfGV6IMMII97tTjqSXeJwPAMEjtbDX'
spreadsheet_id = '13L9OodSo4Gp1vKPKpqEsi8vuoaxefuqhR6adXEvux5o'


gdrive = GDrive(folder_id)
gsheet = GSheet(spreadsheet_id)



def pull_data_from_gsh(sheet_name, gsheet=gsheet):

	df = gsheet.read_from_sheet(sheet_name)
	df = df.drop(columns='No.')

	if 'Blockers' not in list(df.columns): df['Blockers']=""
	df = df.rename(columns={'Role In Project ': 'Role In Project', 
							'Total Hours Available ': 'Total Hours Available',
							'Hours Currently Allocated for Project': 'Hours spent on project this week'})

	df = df[df['Role In Project'] != 'No active role in the project']
	df = df[(df['Role In Project'] != '') | (df['Hours spent on project this week'] != '') | (df['Total Hours Available'] != '') | (df['Skills'] != '') | (df['Tasks Currently Working On'] != '') | (df['Blockers'] != '') | (df['Deliverables for this Week'] != '')]

	df = df.reset_index(drop=True)

	return df[['Name', 'Role In Project', 'Hours spent on project this week', 'Total Hours Available', 'Skills', 'Tasks Currently Working On', 'Blockers', 'Deliverables for this Week']]


def create_presentation(df, file_name='Untitled', table_title='', step = 3, gdrive=gdrive):

	if file_name not in gdrive.get_files_names():
		presentation_id = gdrive.create_google_slides(file_name)
	else:
		presentation_id = gdrive.get_file_id(file_name)

	gslide = GSlide(presentation_id)

	# delete existing slides
	slides_ids = gslide.get_slides_ids()
	for slide_id in slides_ids[:]:
		gslide.slide_delete(slide_id)

	# MASTER SLIDES
	# Add Glasswall logo
	gslide.element_create_image(page_id='p12', image_url='https://i.ibb.co/LPX6FKv/glasswall-logo2.png', x_pos=610, y_pos=-20, width=100, height=100)
	# Add background color
	#gslide.set_slide_background_color(page_id='p12', color='pale-blue')

	slides_ids = []
	k0 = 0
	for k in range(step, len(df)+step, step):
		slide_id = '0000' + str(k)
		slides_ids.append(slide_id)
		# Add table
		gslide.add_slide_with_table_from_df(slide_id, title=table_title, data=df.loc[k0:k-1].reset_index(drop=True))
		k0 = k

	return presentation_id, slides_ids


def tracking_enhancement(presentation_id, slides_ids, gdrive=gdrive):

	gslide = GSlide(presentation_id)

	widths = [50, 65, 90, 60, 100, 120, 80, 120]
	requests = []
	for slide_id, i, w in zip(slides_ids, range(8), widths):
		request = gslide.element_set_table_column_width_request(table_id=slide_id+'_table', column_index=i, column_width=w)
		requests.append(request)

	if len(requests) > 0: gslide.batch_update(requests)


def release_enhancement(presentation_id, slides_ids, gdrive=gdrive):

	gslide = GSlide(presentation_id)

