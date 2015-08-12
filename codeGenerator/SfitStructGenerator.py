#coding=utf8
__author__ = 'xujun'

import sys
from base.RPCStruct import *
from base.RPCParser import *
import sys
import codecs as codecs
import os
from CodeGenerator import parseFile, saveFile
from tools.StringHelper import replace

NEED_STRUCTS = ["CStockInfo", "CAccountInfo", "CXtOrderTag", "CAccountDetail", "COrderDetail", \
                "CDealDetail", "CPositionDetail", "CPositionStatics", "COrderError", "CCancelError", \
                "CGrade", "COtherRight", "CCodeOrderParam", "CProductWorkFlowNode", "CProductWorkFlow",\
                "CProduct", "COrderCommand", "CPriceData", "StockQueryDeliveryResp", "StockQueryAccountStatementResp",\
                "CAccountSettlementInfo", "CFtMarginRateLimit", "CFtProductCompliance", "CFtCombProductPair",\
                "COrderSetting", "CFtInstrumentStopLoss", "CFtAccountStopLoss", "CFtAccountCompliance", "CUserInfo",\
                "CFtConfigAccount", "CGetUserInfoResp", "COrderTag", "COrderInfo", "CTaskOpRecord", "CTaskDetail", "CDealStatics",]

mapToTTserviceTemplate = '''\
    for ({{TYPE_NAME}}::const_iterator cIter = raw.{{FIELD_NAME}}.begin{{}}; cIter != raw.{{FIELD_NAME}}.end{{}}; ++cIter)
    {
        ttservice::{{TTSTRUCT_NAME}} ttStruct;
        to_ttservice_struct(cIter->second, ttStruct);
        ret.{{FIELD_NAME}}.insert(make_pair(cIter->first, ttStruct));
    }'''

mapToXtiTemplate = '''\
    for ({{TYPE_NAME}}::const_iterator cIter = raw.{{FIELD_NAME}}.begin{{}}; cIter != raw.{{FIELD_NAME}}.end{{}}; ++cIter)
    {
        {{XTI_NAME}} xtStruct;
        to_xti_struct(cIter->second, xtStruct);
        ret.{{FIELD_NAME}}.insert(make_pair(cIter->first, xtStruct));
    }'''


vectorToTTserviceTemplatePtr ='''\
    ret.{{FIELD_NAME}}.resize(raw.{{FIELD_NAME}}.size{{}});
    for (size_t i = 0;i < raw.{{FIELD_NAME}}.size{{}}; ++i)
    {
        ttservice::{{TTSTRUCT_NAME}} ttStruct(new ttservice::{{NO_PTR}});
        to_ttservice_struct(raw.{{FIELD_NAME}}[i], *ttStruct);
        ret.{{FIELD_NAME}}[i] = ttStruct;
    }'''


vectorToXtiTemplatePtr = '''\
    ret.{{FIELD_NAME}}.resize(raw.{{FIELD_NAME}}.size{{}});
    for (size_t i = 0;i < raw.{{FIELD_NAME}}.size{{}}; ++i)
    {
        {{XTI_NAME}} xtStruct;
        to_xti_struct(raw.{{FIELD_NAME}}[i], xtStruct);
        ret.{{FIELD_NAME}}[i] = xtStruct;
    }'''

vectorToTTserviceTemplate ='''\
    ret.{{FIELD_NAME}}.resize(raw.{{FIELD_NAME}}.size{{}});
    for (size_t i = 0;i < raw.{{FIELD_NAME}}.size{{}}; ++i)
    {
        ttservice::{{TTSTRUCT_NAME}} ttStruct;
        to_ttservice_struct(raw.{{FIELD_NAME}}[i], ttStruct);
        ret.{{FIELD_NAME}}[i] = ttStruct;
    }'''


vectorToXtiTemplate = '''\
    ret.{{FIELD_NAME}}.resize(raw.{{FIELD_NAME}}.size{{}});
    for (size_t i = 0;i < raw.{{FIELD_NAME}}.size{{}}; ++i)
    {
        {{XTI_NAME}} xtStruct;
        to_xti_struct(raw.{{FIELD_NAME}}[i], xtStruct);
        ret.{{FIELD_NAME}}[i] = xtStruct;
    }'''


class SfitStructCodeGenerator:
    def __init__(self, desc, typeManager):
        self.desc = desc
        self.typeManager = typeManager

    def getStruct(self, structName):
        for astruct in self.desc.structs:
            if astruct.name == structName:
                return astruct
        return None


    def genHCodes(self):
        ret = '''\
/********************************************************************
    company:    北京睿智融科控股有限公司
    fileName:	XtStructs.h
    author:		xujun
    created:	8:11:2013   15:14
    purpose:	结构定义
*********************************************************************/
#ifndef XtStructs_2013_11_8_H
#define XtStructs_2013_11_8_H

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "XtDef.h"
#include "XtDataType.h"

namespace xti
{
{{StructCodes}}
}

#endif
'''
        ret = replace(ret, u"{{StructCodes}}", self.genHStructCodes(0))
        return ret

    def genHStructCodes(self, offset):
        structTemplate = '''\
    struct XT_API_EXPORT {{StructName}}
    {
        {{StructName}}();
        {{FieldCodes}}
    };
'''
        structsCodes = []
        for astruct in self.desc.structs:
            str = structTemplate
            lines = []
            for item in astruct.items:
                typeName = item.type.getTypeName()
                if typeName.endswith("Ptr"):
                    typeName = typeName[0:-3]
                if typeName.find("bson::bo") != -1:
                    typeName = u"std::string"
                line = u"%s %s;" % (typeName, item.name)
                if len(item.comment) > 0 : line += u" //" + item.comment
                lines.append(line)
            strContent = u"\n".join(lines)
            str = replace(str, "{{FieldCodes}}", strContent)
            str = replace(str, "{{StructName}}", astruct.name)
            str = replace(str, "{{Namespace}}::", "")
            str = replace(str, "Ptr", "")
            structsCodes.append(str)
        return "\n".join(structsCodes)

    def genCppCodes(self):
        strTemplate = '''\
#include "XtStructs.h"
#include "utils/commonFunc.h"

namespace xti
{
{{StructCodes}}
}
    '''
        ret = strTemplate
        ret = replace(ret, u"{{StructCodes}}", self.genCppStructCodes(0))
        return ret

    def genCppStructCodes(self, offset):
        structTemplate = '''\
        {{StructName}}::{{StructName}}()
        {{InitCode}}
        {
        }
    '''
        structsCodes = []
        for astruct in self.desc.structs:
            str = structTemplate
            initCode = u",\n".join([ u"%s(%s)" % (item.name, u"utils::getInvalidValue<%s>()" % item.type.getTypeName() if len(item.default) == 0 else item.default)\
                                     for item in astruct.items if item.type.isNeedInit() or len(item.default) > 0 ])
            if len(initCode) > 0 :
                initCode = ":" + initCode
            str = replace(str, "{{InitCode}}", initCode)
            str = replace(str, "{{StructName}}", astruct.name)
            str = replace(str, "ttservice::", "")
            structsCodes.append(str)
        return "\n".join(structsCodes)

    def genTranslatorHCodes(self, offset):
        template = '''\
/********************************************************************
	company:    北京睿智融科控股有限公司
	fileName:	Translator.cpp
	author:		xujun
	created:	11:11:2013   13:47
	purpose:	结构翻译
*********************************************************************/
#ifndef Translator_2013_11_11_H
#define Translator_2013_11_11_H

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "Protocol/rpc_Structs.h"
#include "Protocol/rpc_StockCommon.h"
#include "Protocol/rpc_ClientTraderCommon.h"
#include "XtStructs.h"

namespace xti
{
    {{StructCodes}}
}

#endif
        '''
        codes = []
        for astruct in NEED_STRUCTS:
            code = '''\
// {{StructName}}
void to_ttservice_struct(const {{StructName}}& raw, ttservice::{{StructName}}& ret);
void to_xti_struct(const ttservice::{{StructName}}& raw, {{StructName}}& ret);
void to_xti_struct(const ttservice::IDataPtr& raw, {{StructName}}& ret);
            '''
            code = code.replace("{{StructName}}", astruct)
            codes.append(code)
        strCode = "\n".join(codes)
        ret = template
        ret = replace(ret, "{{StructCodes}}", strCode)
        return ret

    def genTranslatorCppCodes(self, offset):
        template = u'''
#include "implement/Translator.h"
#include "bson/src/util/json.h"

namespace xti
{
    {{StructCodes}}
}
        '''
        codes = []
        for structName in NEED_STRUCTS:
            code = u'''\
// {{StructName}}
void to_ttservice_struct(const {{StructName}}& raw, ttservice::{{StructName}}& ret)
{
{{ToTTCodes}}
}
void to_xti_struct(const ttservice::{{StructName}}& raw, {{StructName}}& ret)
{
{{ToXtiCodes}}
}

void to_xti_struct(const ttservice::IDataPtr& raw, {{StructName}}& ret)
{
    boost::shared_ptr<ttservice::{{StructName}}> ptrRaw = boost::shared_dynamic_cast<ttservice::{{StructName}}>(raw);
    if (NULL != ptrRaw) to_xti_struct(*ptrRaw, ret);
}
            '''
            astruct = self.getStruct(structName)
            if astruct == None:
                continue

            toTTItems = []
            toXtiItems = []
            for item in astruct.items:
                enumType = ""
                typeName = item.type.getTypeName()
                str1 = u""
                str2 = u""
                if typeName.startswith("std::vector") and typeName.find("{{Namespace}}::") != -1:
                    pos = typeName.find("{{Namespace}}::") + 15
                    structType = item.type.getTypeName()
                    if typeName.find("Ptr") != -1:
                        str1 = vectorToTTserviceTemplatePtr.replace("{{FIELD_NAME}}", item.name).replace("{{TTSTRUCT_NAME}}", typeName[pos:-2]).replace("{{NO_PTR}}", typeName[pos:-5])
                        str2 = vectorToXtiTemplatePtr.replace("{{FIELD_NAME}}", item.name).replace("{{XTI_NAME}}", typeName[pos:-5])
                    else:
                        str1 = vectorToTTserviceTemplate.replace("{{FIELD_NAME}}", item.name).replace("{{TTSTRUCT_NAME}}", typeName[pos:-2])
                        str2 = vectorToXtiTemplate.replace("{{FIELD_NAME}}", item.name).replace("{{XTI_NAME}}", typeName[pos:-2])
#                    if typeName.find("Ptr") != -1:
#                        str1 = str1.replace("{{*}}", "*")
#                        str2 = str2.replace("{{*}}", "*")
#                    else:
#                        str1 = str1.replace("{{*}}", "")
#                        str2 = str2.replace("{{*}}", "")
                elif typeName.find("bson::bo") != -1:
                    str1 = u"    ret.%s = bson::fromjson(raw.%s);" % (item.name, item.name)
                    str2 = u"    ret.%s = raw.%s.toString{{}};" % (item.name, item.name)
                elif typeName.startswith("std::map") and typeName.find("{{Namespace}}::") != -1:
                    #pass
                    pos = typeName.find("{{Namespace}}::") + 15
                    str1 = mapToTTserviceTemplate.replace("{{TYPE_NAME}}", typeName.replace("{{Namespace}}::", "")).replace("{{FIELD_NAME}}", item.name).replace("{{TTSTRUCT_NAME}}", typeName[pos:-2])
                    str2 = mapToXtiTemplate.replace("{{TYPE_NAME}}", typeName.replace("{{Namespace}}::", "ttservice::")).replace("{{FIELD_NAME}}", item.name).replace("{{XTI_NAME}}", typeName[pos:-2])
                else:
                    if typeName.startswith("{{Namespace}}::"):
                        if typeName.endswith("Ptr"):
                            str1 = u"    ret.%s = %s(new %s); to_ttservice_struct(raw.%s, *ret.%s);" % (item.name, typeName, typeName[0:-3], item.name, item.name)
                            str2 = u"    if (NULL != raw.%s) to_xti_struct(*raw.%s, ret.%s);" % (item.name, item.name, item.name)
                        else:
                            rawTypeName = typeName[len("{{Namespace}}::"):]
                            if rawTypeName.startswith("E"):
                                enumType = item.type.getTypeName()
                                str1 = u"    ret.%s = (%s)raw.%s;" % (item.name, enumType, item.name)
                                str2 = u"    ret.%s = (%s)raw.%s;" % (item.name, enumType, item.name)
                            else:
                                str1 = u"    to_ttservice_struct(raw.%s, ret.%s);" % (item.name, item.name)
                                str2 = u"    to_xti_struct(raw.%s, ret.%s);" % (item.name, item.name)
                    else:
                        str1 = u"    ret.%s = (%s)raw.%s;" % (item.name, enumType, item.name)
                        str2 = u"    ret.%s = (%s)raw.%s;" % (item.name, enumType, item.name)

                str1 = str1.replace("{{Namespace}}", "ttservice")
                str2 = str2.replace("{{Namespace}}", "xti")
                toTTItems.append(str1)
                toXtiItems.append(str2)
            strToTTCodes = "\n".join(toTTItems)
            strToTxiCodes = "\n".join(toXtiItems)
            code = code.replace("{{ToTTCodes}}", strToTTCodes)
            code = code.replace("{{ToXtiCodes}}", strToTxiCodes)
            code = code.replace("{{StructName}}", structName)
            code = code.replace("()", "")
            code = code.replace("{{}}", "()")
            codes.append(code)
        strCode = "\n".join(codes)
        ret = template
        ret = replace(ret, "{{StructCodes}}", strCode)
        return ret

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding( "utf-8" )

    sys.argv = ["",\
                "E:\\SVN\\ttservice\\branches\\traderapi_20131114\\libs\\traderbase\\src\\Protocol\\rpc", \
                "E:\\SVN\\ttservice\\branches\\traderapi_20131114\\src\\XtTraderApi"\
                ]

    dir = sys.argv[1]
    basePath = dir + "/Structs.rpc"
    ftPath = dir + "/FtCommon.rpc"
    stockPath = dir + "/StockCommon.rpc"
    clientTraderPath = dir + "/ClientTraderCommon.rpc"
    outDir = sys.argv[2]

    typeManager = StdTypeManger()
    base_desc = parseFile(basePath, typeManager)
    ft_desc = parseFile(ftPath, typeManager)
    stock_desc = parseFile(stockPath, typeManager)
    clientTrader_desc = parseFile(clientTraderPath, typeManager)

    total_desc = base_desc
    total_desc.structs = base_desc.structs + ft_desc.structs + stock_desc.structs + clientTrader_desc.structs
    desc = total_desc
    desc = RPCDescript()
    for name in NEED_STRUCTS:
        for astruct in total_desc.structs:
            print astruct.name, name
            if astruct.name == name:
                desc.structs.append(astruct)
                break

    generator = SfitStructCodeGenerator(desc, typeManager)

    hCodes = generator.genHCodes()
    saveFile(outDir + "/XtStructs.h", hCodes);

    cppCodes = generator.genCppCodes()
    saveFile(outDir + "/implement/XtStructs.cpp", cppCodes);

    cppCodes = generator.genTranslatorHCodes(0)
    saveFile(outDir + "/implement/Translator.h", cppCodes);

    cppCodes = generator.genTranslatorCppCodes(0)
    saveFile(outDir + "/implement/Translator.cpp", cppCodes);

