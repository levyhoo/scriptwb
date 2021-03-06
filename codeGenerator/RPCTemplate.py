#coding=utf8
_author_ = 'Administrator'

FILE_TEMPLATE_SERVICE_HPP = u'''\
/**
  WARNING :
  This file is generated by python script.
  DO NOT MODIFY!
*/

#ifndef {{ServiceName}}_{{tag}}_H_
#define {{ServiceName}}_{{tag}}_H_
#include "net/RPCServer.h"
#include "utils/TTError.h"
{{IncludeFiles}}
{{IncludeCodes}}
{{ConstDefineCodes}}
{{EnumStructCodes}}
{{ClassCodes}}

#endif //{{ServiceName}}_H_
'''

FILE_TEMPLATE_CLIENT_HPP = u'''\
/**
  WARNING :
  This file is generated by python script.
  DO NOT MODIFY!
*/

#ifndef {{ServiceName}}_{{tag}}_H_
#define {{ServiceName}}_{{tag}}_H_
#include "utils/STLHelper.h"
#include "net/RPCClient.h"
#include "utils/TTError.h"
#include "net/RPCParamBuilder.h"
{{IncludeFiles}}
#include <boost/signals2.hpp>
{{IncludeCodes}}
{{ConstDefineCodes}}
{{EnumStructCodes}}
{{ClassCodes}}

#endif //{{ServiceName}}_H_
'''

FILE_TEMPLATE_STRUCT_HPP = u'''\
/**
  WARNING :
  This file is generated by python script.
  DO NOT MODIFY!
*/

#ifndef {{ServiceName}}_{{tag}}_H_
#define {{ServiceName}}_{{tag}}_H_
#include "utils/STLHelper.h"
#include "utils/TTError.h"
#include "utils/DefaultValue.h"
{{IncludeFiles}}
{{IncludeCodes}}
{{ConstDefineCodes}}
{{EnumStructCodes}}
{{ClassCodes}}

#endif //{{ServiceName}}_H_
'''

FILE_TEMPLATE_CPP = u'''\
/**
  WARNING :
  This file is generated by python script.
  DO NOT MODIFY!
*/
#include "{{HPP_OUT_FILE}}"
#include "utils/TrafficWatch.h"
#include "net/NetPackageAlloc.h"

{{IncludeCodes}}

{{StructCodesService}}

{{ClassCodes}}

'''

CONST_DEFINE_TEMPLATE = u'''\
// const defines
namespace {{Namespace}}
{
    {{CostDefineContentCodes}}
}\
'''

ENUM_AND_STRUCT_TEMPLATE_HPP = u'''
namespace {{Namespace}}
{
    // enum defines
    {{EnumCodes}}

    // struct index
    {{StructIds}}

    // struct defines
    {{StructCodes}}

    {{RegisterCodes}}
};

namespace utils
{
    // enums ref
    {{EnumBsonCodes}}
    // struct ref
    {{StructBsonCodes}}
    // enums ref
    {{EnumDefaultCodes}}
};
'''

ENUM_AND_STRUCT_TEMPLATE_CPP = u'''
namespace {{Namespace}}
{
    // struct index
    {{StructIds}}

    // struct defines
    {{StructCodes}}
};
'''
CLASS_TEMPLATE = u'''\
namespace {{Namespace}}
{
    // class
    {{ClassCodes}}
};
'''

ENUM_TEMPLATE = u'''\
enum {{TypeName}}
{
{{Content}}
};'''

STRUCT_BASE_TEMPLATE_HPP = u'''\
struct {{ExportMacro}} {{TypeNameWithInherit}}
{
    {{TypeName}}();
    void bsonValueFromObj(bson::bo obj);
    void appendElements(bson::bob& objBuilder) const;

    {{Content}}
};
{{PropertyDesc}}
'''

STRUCT_BASE_TEMPLATE_CPP = u'''\
{{TypeNameWithInherit}}::{{TypeNameWithInherit}}()
{{InitCode}}
{};

void {{TypeNameWithInherit}}::bsonValueFromObj(bson::bo obj)
{
    {{ParserBson}}
};

void {{TypeNameWithInherit}}::appendElements(bson::bob& objBuilder) const
{
    {{AppendToBuilder}}
};
'''

STRUCT_IDATA_TEMPLATE = u'''\
class {{ExportMacro}} {{TypeNameWithInherit}}
{
public:
    {{TypeName}}();
    {{Func}}

    {{Content}}

    {{Statics}}

    static StructDes s_desc;
};

{{PropertyDesc}}
'''

STRUCT_IDATA_TEMPLATE_NO_PARSER = u'''\
class {{ExportMacro}} {{TypeNameWithInherit}}
{
public:
    {{TypeName}}();
    void bsonValueFromObj(bson::bo obj);
    void appendElements(bson::bob& objBuilder) const;
    void appendElementsWithNoTypeId(bson::bob& objBuilder) const;

    {{Func}}

    {{Content}}

    {{Statics}}

    static StructDes s_desc;
};

{{PropertyDesc}}
'''

ENUM_BSON_TEMPLATE = u'''\
ENUM_BSON_BUILDER_DECLEAR({{Namespace}}::{{TypeName}});
'''

STRUCT_BSON_TEMPLATE = u'''\
OBJ_BSON_BUILDER_DECLEAR({{Namespace}}::{{TypeName}});
'''

STRUCT_GETDESCMAP_FUNC_DECLEAR = u'''
// 用于数据排重
virtual ostringstream& toStream(ostringstream& os) const;
static string genKey({{KeyParam}});
// 用于日志打印
virtual ostringstream& toLogStream(ostringstream& os) const;
// 取得结构说明
virtual const StructDes& getStructDes() const;
// 拷贝
virtual IDataPtr copy() const ;
inline bool operator ==(const {{TypeName}}& right) const {return this->isEqual(&right);};
'''

STRUCT_DECLEAR_TEMPLATE = u'''\
{{Func}}
'''


STRUCT_GETDESCMAP_FUNC = u'''\
//////////////////////////////
///{{TypeName}}
////////////////////////////////
{{Statics}}
StructDes {{TypeName}}::s_desc;

{{FieldParses}}

{{TypeName}}::{{TypeName}}()
    {{InitCode}}
{};

const StructDes& {{TypeName}}::getStructDes() const
{
	return {{TypeName}}::s_desc;
}

IDataPtr {{TypeName}}::copy() const
{
    {{TypeName}}Ptr ret(new {{TypeName}}(*this));
    return ret;
}

string {{TypeName}}::genKey( {{KeyParam}})
{
    ostringstream os;
    {{GenKey}}
    return os.str();
}

ostringstream& {{TypeName}}::toStream(ostringstream& os) const {
    {{ToStream}}
    return os;
}

ostringstream& {{TypeName}}::toLogStream(ostringstream& os) const {
    {{ToLog}}
    return os;
}

'''

STRUCT_GETDESCMAP_FUNC_NO_PARSE = u'''\
//////////////////////////////
///{{TypeName}}
////////////////////////////////
{{Statics}}
StructDes {{TypeName}}::s_desc;
#ifdef USE_OBJECT_POOL
boost::object_pool<{{TypeName}}> {{TypeName}}::_objpool;
boost::mutex {{TypeName}}::_mutex_{{TypeName}};
#endif

{{TypeName}}::{{TypeName}}()
    {{InitCode}}
{};

const FieldDes& {{TypeName}}::getFieldDes(int id) const
{
    const map<int, FieldDes>& desc = getFieldDes();
    return utils::getMapValueConstRef(desc, id);
}

const map<int, FieldDes>& {{TypeName}}::getFieldDes() const
{
	return {{TypeName}}::s_desc.m_fields;
}

const StructDes& {{TypeName}}::getStructDes() const
{
	return {{TypeName}}::s_desc;
}

static map<int, int> gen_{{TypeName}}_offsets()
{
    {{TypeName}} t;
    map<int, int> ret;
    {{GenOffsetCodes}}
    return ret;
}

IDataPtr {{TypeName}}::copy() const
{
    {{TypeName}}Ptr ret(new {{TypeName}}(*this));
    return ret;
}

string {{TypeName}}::genKey( {{KeyParam}})
{
    ostringstream os;
    {{GenKey}}
    return os.str();
}

void {{TypeName}}::appendElements(bson::bob& objBuilder) const
{
    utils::appendToBuilder(objBuilder, "_typeId", (int)XT_{{TypeName}});
    appendElementsWithNoTypeId(objBuilder);
};

ostringstream& {{TypeName}}::toStream(ostringstream& os) const {
    {{ToStream}}
    return os;
}

ostringstream& {{TypeName}}::toLogStream(ostringstream& os) const {
    {{ToLog}}
    return os;
}
'''

STRUCT_DESCMAP_FUNC = u'''\
	static StructDes _desc = StructDes({{TypeEnum}}, {{BaseTypeEnum}}, "{{TypeName}}", descMap());
'''
STRUCT_CPP_FILE_TEMPLATE_SERVICE_CPP = u'''\
#include "common/Stdafx.h"
#include "rpc_{{ServiceName}}.h"
{{IncludeCodes}}
{{LuaHeaderCodes}}

namespace {{Namespace}}
{
    {{StructCodes}}

    {{EnumDeclears}}
    {{StructDeclears}}

    int regist_{{ServiceName}}()
    {
        static bool s_isRegisted = false;
        if (s_isRegisted)
            return 0;
        s_isRegisted = true;
        {{RegisterCodes}}
        return 0;
    }

    {{EnumRegisters}}
    {{StructRegisters}}
};
'''

ONE_ENUM_REGIST_TEMPLATE = u'''\
void regist_enum_{{EnumName}}()
{
    {{EnumCodes}}
}
'''

ONE_ENUM_ITEM_REGIST_TEMPLATE = u'''ttservice::TypeManager::instance()->registerEnum("{{EnumName}}", {{ItemValue}}, "{{ItemName}}");'''

ONE_STRUCT_REGIST_TEMPLATE = u'''\
void regist_struct_{{TypeName}}()
{
    using namespace utils;
    map<int, FieldDes> desc;
    {{TypeName}} self;
    {{FieldInfos}}
    {{BaseInfoCodes}}
    StructDes sd(XT_{{TypeName}}, {{BaseTypeId}}, "{{TypeName}}", desc);
    {{TypeName}}::s_desc = sd;
    IDataCreatorPtr creator = IDataCreatorPtr(new TypeCreator<{{TypeName}}>());
    TypeManager::instance()->registerType(sd, creator);
}
'''

INITI_FIELDDES = u'''
{
    FieldDes fdes;
    fdes.m_nId = {{TypeName}}::ITEM_{{ID}};
    fdes.m_nType = {{TYPE}};
    fdes.m_propertys = {{propertys}};
    fdes.m_funcs = {{funcs}};
    fdes.m_strFieldName = \"{{fieldName}}\";
    fdes.m_parser = FieldParsePtr(new {{TypeName}}_{{parser}}());
    fdes.m_dPrecision = {{precision}};
    fdes.m_iFlag = {{flag}};
    fdes.m_nIDataId = {{nIDataId}};
    fdes.m_strTypeName = \"{{TYPE_NAME}}\";
    fdes.init(\"{{NAME}}\", \"{{visible}}\");
    fdes.m_nOffset = ;
    desc.insert(make_pair({{TypeName}}::ITEM_{{ID}}, fdes));
}
'''

IF_ELSE_FIXED = u'''\
bool update = false;
memset(sql, 0, sizeof(sql));
{{SPRINT_SELECT}}
if(!mysql_query(mysql, sql))
    {
    MYSQL_RES *results = mysql_store_result(mysql);
if(results)
    {
    MYSQL_ROW sqlrow = mysql_fetch_row(results);
if(NULL != sqlrow)
    {
    update = true;
}
}
mysql_free_result(results);
}
else
    {
    cout<<"mysql_query error,"<<mysql_error(mysql)<<endl;
continue;
}

//
memset(sql, 0, sizeof(sql));
'''

#    {{CREATE_ALL_TABLE}}
#if(mysql_real_query(mysql, createStr, strlen(createStr)) ){
#   cout<<"mysql_query error,"<<mysql_error(mysql)<<endl;
#Ecout<<createStr<<endl;
#}

FILE_MAIN_SQL =u'''\
#include <redisclient.h>
#include <bson/src/bson.h>
#include <log4cxx/logger.h>
#include <log4cxx/propertyconfigurator.h>
#include <mysql/mysql.h>
#include "utils/Config.h"
#include "utils/convFunc.h"
#include "Protocol/rpc_ClientTrader.h"
#include "Protocol/rpc_Structs.h"
#include "Protocol/rpc_ClientTraderCommon.h"

using namespace boost;
using namespace std;

using namespace log4cxx;
using namespace utils;

string seconds2date(int seconds)
{
    time_t _seconds = seconds;
    r_int64 _time;
    struct tm tt;
    localtime_r(&_seconds, &tt);
    char buf[40] = {0};
    sprintf(buf, "%04d%02d%02d", tt.tm_year + 1900, tt.tm_mon + 1, tt.tm_mday);

    string date = buf;
    return date;
}

int main(int argc, char* argv[])
{
	if( argc != 2 )
	{
		cout<<"usage:"<<endl;
		cout<<"      "<<argv[0]<<" scanTask.ini"<<endl;
		return -1;
	}

	boost::shared_ptr<Configuration> m_config = boost::shared_ptr<Configuration>(new Configuration((const char*)argv[1]));
	m_config->load();
	string host = m_config->read("redis", "host");

	string ip = m_config->read("mysql", "ip");
	unsigned int port = m_config->readInt("mysql", "port", 3306);
	string user = m_config->read("mysql", "user");
	string pass = m_config->read("mysql", "pass");
	string db = m_config->read("mysql", "db");

	//connect redis
	boost::shared_ptr<redis::client> m_redis;
	try
	{
		m_redis.reset( new redis::client(host) );
	}
	catch(redis::redis_error e)
	{
		cerr<<e.what()<<endl;
		return -1;
	}

	//connect mysql
	MYSQL* mysql = NULL;
	if ( ( mysql = mysql_init(NULL))
		&& mysql_real_connect( mysql, ip.c_str(), user.c_str(), pass.c_str(), db.c_str(), port, NULL, CLIENT_MULTI_STATEMENTS ) )
	{
		if (mysql_set_server_option(mysql, MYSQL_OPTION_MULTI_STATEMENTS_ON))
		{
			cerr<<"mysql_set_server_option error"<<endl;
			return -1;
		}

		my_bool reconnect = 1;
		if (mysql_options(mysql, MYSQL_OPT_RECONNECT, &reconnect))
		{
			cerr<<"mysql_options error"<<endl;
			return -1;
		}
	}
	else
	{
		cerr<<"mysql_real_connect error,"<<mysql_error(mysql)<<endl;
		return -1;
	}

	//scan redis
	vector<string> vkey;
	char buf[1024] = {0};
	string strDate = seconds2date(time(NULL));
	sprintf(buf, "*detailInfos*");
	m_redis->keys(buf, vkey);
	for(size_t i=0; i<vkey.size(); i++)
	{
	    string strdata = m_redis->get(vkey[i]);
	    bson::bo bsobj(strdata.c_str());
	    {{VALUE_INITE}}
	    ttservice::CFtAccountDetail accountDetail;
	    utils::safeParseBson(bsobj.copy(), "accounts", accountDetail);
	    char sql[4096] = {0};
		{{UPDATE_CODES}}
		return 0;
	}
}
'''

import re
line = "2013-11-19 01:16:06,379 [INFO] inSize 289 outSize 210 rate 72.664360 time 0.102997 makeBsonPack COMPRESS_ZLIB"
m = re.search("inSize\s(?P<insize>.*)\soutSize\s(?P<outsize>.*)\srate.*time\s(?P<second>.*)\smake", line)
print m
print m.group("insize")
print m.group("outsize")
print m.group("second")
