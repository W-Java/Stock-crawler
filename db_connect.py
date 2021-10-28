import pymysql

###导入数据库的具体函数操作
def InsertData(TableName, dic):
    try:
        #连接数据库
        conn = pymysql.connect(host='localhost', user='root', password='010625', db='datatest', port=3306)  # 链接数据库
        #创建游标对象
        cur = conn.cursor()
        COLstr = ''  # 列的字段
        ROWstr = ''  # 行字段

        ColumnStyle = ' VARCHAR(20)'
        for key in dic.keys():
            COLstr = COLstr + ' ' + key + ColumnStyle + ','
            ROWstr = (ROWstr + '"%s"' + ',') % (dic[key])

        # 判断表是否存在，存在执行try，不存在执行except新建表，再insert
        try:
            cur.execute("SELECT * FROM  %s" % (TableName))
            cur.execute("INSERT INTO %s VALUES (%s)" % (TableName, ROWstr[:-1]))

        except pymysql.Error as e:
            cur.execute("CREATE TABLE %s (%s)" % (TableName, COLstr[:-1]))
            cur.execute("INSERT INTO %s VALUES (%s)" % (TableName, ROWstr[:-1]))
        #提交到数据库执行
        conn.commit()
        #关闭游标
        cur.close()
        #关闭数据库
        conn.close()

    except pymysql.Error as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))