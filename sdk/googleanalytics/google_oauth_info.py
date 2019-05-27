"""Hello Analytics Reporting API V4."""

import argparse
from apiclient import discovery
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
CLIENT_SECRETS_PATH = 'client_secrets.json'
# Path to client_secrets.json file.
VIEW_ID = '195776851'


def initialize_analyticsreporting():
    """
    Initializes the analyticsreporting service object.
    Returns:
    analytics an authorized analyticsreporting service object.
    """
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     parents=[tools.argparser])
    flags = parser.parse_args([])

    # Set up a Flow object to be used if we need to authenticate.
    flow = client.flow_from_clientsecrets(CLIENT_SECRETS_PATH,
                                          scope=SCOPES,
                                          message=tools.message_if_missing(CLIENT_SECRETS_PATH))

    storage = file.Storage('analyticsreporting.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())
    # Build the service object.
    analytics = discovery.build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)
    print(analytics)
    return analytics


def get_report(analytics):
    # Use the Analytics Service Object to query the Analytics Reporting API V4.
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:sessions'}],
                    'dimensions': [{'name': 'ga:country'}]
                }]
        }
    ).execute()


def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response"""
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        print(columnHeader)
        dimensionHeaders = columnHeader.get('dimensions', [])
        print(dimensionHeaders)
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])
        print(rows)

        for row in rows:
            dimensions = row.get('dimensions', [])
            print(dimensions)
            dateRangeValues = row.get('metrics', [])
            print(dateRangeValues)

            for header, dimension in zip(dimensionHeaders, dimensions):
                print(header + ': ' + dimension)

            for i, values in enumerate(dateRangeValues):
                print('Date range (' + str(i) + ')')
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    print(metricHeader.get('name') + ': ' + value)


def main():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    print_response(response)


if __name__ == '__main__':
    main()
