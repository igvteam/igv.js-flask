import sys
import re
from flask import request, jsonify
from igvjs.services import services_blueprint

# ucsc route
@services_blueprint.route('/ucsc')
def query_ucsc():
    if 'mysql.connector' not in sys.modules:
        if services_blueprint.ucsc_enabled:
            try:
                import mysql.connector
            except ImportError:
                return 'UCSC service is enabled but mysql.connector is not installed. Please \
        install mysql-connector (pip install mysql-connector==2.1.4) if you wish to use the UCSC service.'
        else:
            return 'You have not enabled the UCSC library. Please enable it in \
_config.py and make sure to install mysql-connector (pip install mysql-connector==2.1.4).'

    results = []

    def reg2bins(beg, end):
        bin_list = []
        end -= 1
        bin_list.append(0)
        for k in xrange(1 + (beg >> 26), 2 + (end >> 26)):
            bin_list.append(k)
        for k in xrange(9 + (beg >> 23), 10 + (end >> 23)):
            bin_list.append(k)
        for k in xrange(73 + (beg >> 20), 74 + (end >> 20)):
            bin_list.append(k)
        for k in xrange(585 + (beg >> 17), 586 + (end >> 17)):
            bin_list.append(k)
        for k in xrange(4681 + (beg >> 14), 4682 + (end >> 14)):
            bin_list.append(k)
        return bin_list

    db = request.args.get('db')
    table = request.args.get('table')
    genomic_range = request.args.get('genomic_range')

    ucsc_host = 'genome-mysql.soe.ucsc.edu'
    ucsc_user = 'genome'

    m = re.search('(chr\d+)', genomic_range)
    chrom = m.group(1)

    try:
        connection = mysql.connector.connect(host=ucsc_host, user=ucsc_user, database=db)
        cur = connection.cursor()

        cur.execute("SELECT * FROM information_schema.COLUMNS \
WHERE TABLE_NAME = %s AND COLUMN_NAME = 'bin' LIMIT 1", (table,))

        if cur.fetchone():
            m = re.search(chrom+':(\d+)-(\d*)', genomic_range)
            if m:
                start = int(m.group(1))
                end = int(m.group(2))

            bins = reg2bins(start, end)
            bin_str = '('+','.join(str(bin) for bin in bins)+')'

            cur.execute("SELECT * FROM "+table+" WHERE chrom = %s \
AND bin in "+bin_str, (chrom,))

        else:
            cur.execute("SELECT * FROM "+table+" WHERE chrom = %s", (chrom,))

        for row in cur.fetchall():
            row_dict = {}
            for name, value in zip(cur.description, row):
                row_dict[name[0]] = str(value)
            results.append(row_dict)

        cur.close()
        connection.close()

    except mysql.connector.Error, e:
        try:
            return "mysql Error [{}]: {}".format(e.args[0], e.args[1])
        except IndexError:
            return "mysql Error: {}".format(str(e))

    return jsonify(results)
