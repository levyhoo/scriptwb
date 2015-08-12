#coding=utf8
__author__ = 'Administrator'

SERVER_INCLUDE_TEMPLATE = u'''\
#include "net/RPCServer.h"
#include "utils/BsonHelper.h"
#include "utils/commonFunc.h"
#include "net/RPCCommon.h"
#include "utils/TrafficWatch.h"
#include "net/RPCServer.h"
#include "net/RPCEngine.h"
 '''

# HPP File Template
SERVER_CLASS_TEMPLATE_HPP = \
u'''\
class {{ExportMacro}} rpc_{{ServiceName}}_server
{
public:
    boost::shared_ptr<net::RPCServer> m_server;

    rpc_{{ServiceName}}_server();
    rpc_{{ServiceName}}_server(boost::shared_ptr<net::RPCServer> server);

    {{VirtualFuncDeclear}}
    {{VirtualSubDeclear}}
    virtual void onConnected(const boost::shared_ptr<net::NetConnection> &pConnection ) {};
    virtual void onError(const boost::shared_ptr<net::NetConnection> &pConnection ) {};

    void regist();
    std::map<std::string, net::ProcessFunc> genFuncMap();

    virtual bool testConnection(std::string function, bson::bo _response, r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection);
    virtual bson::bo do_onConnected( const bson::bo &param, const r_int64 seq, const boost::shared_ptr<net::NetConnection> &pConnection );
    virtual bson::bo do_onError( const bson::bo &param, const r_int64 seq, const boost::shared_ptr<net::NetConnection> &pConnection );

    {{FunctionContent}}

    {{PushFunctionContent}}

    {{SubFunctionContent}}
};\
'''

SERVER_FUNCTION_TEMPLATE_HPP =\
u'''\
bson::bo _{{FuncName}}(const bson::bo &_response, const r_int64 _seq, const boost::shared_ptr<net::NetConnection> &_connection);
static void send_{{FuncName}}({{SendOutParam}} bson::bo _error, r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection, r_uint8 compress = COMPRESS_NONE);\
'''

SERVER_PUSH_FUNCTION_TEMPLATE_HPP =\
u'''\
static void push_{{FuncName}}({{Params1}} const boost::shared_ptr<net::NetConnection> &_connection, r_uint8 compress = COMPRESS_NONE);
void pushAll_{{FuncName}}({{Params2}});\
'''

SERVER_SUB_FUNCTION_TEMPLATE_HPP =\
u'''\
bson::bo _{{FuncName}}(const bson::bo &_response, const r_int64 _seq, const boost::shared_ptr<net::NetConnection> &_connection);
bson::bo _{{FuncName}}_unsub(const bson::bo &_response, const r_int64 _seq, const boost::shared_ptr<net::NetConnection> &_connection);
static void send_{{FuncName}}({{SendOutParam}} r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection, r_uint8 compress = COMPRESS_NONE);
static void send_{{FuncName}}_unsub(bool success, r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection);
'''

# CPP File Template
SERVER_CLASS_TEMPLATE_CPP =\
u'''\
rpc_{{ServiceName}}_server::rpc_{{ServiceName}}_server()
:m_server()
{
}

rpc_{{ServiceName}}_server::rpc_{{ServiceName}}_server(boost::shared_ptr<net::RPCServer> server)
:m_server(server)
{
    regist();
}

void rpc_{{ServiceName}}_server::regist()
{
    if (m_server)
    {
        m_server->setFuncTable(genFuncMap());
        m_server->registerFunc("onConnected", boost::bind(&rpc_{{ServiceName}}_server::do_onConnected, this, _1, _2, _3));
        m_server->registerFunc("onError", boost::bind(&rpc_{{ServiceName}}_server::do_onError, this, _1, _2, _3));
    }
}

std::map<std::string, net::ProcessFunc> rpc_{{ServiceName}}_server::genFuncMap()
{
    std::map<std::string, net::ProcessFunc> ret;
    {{RegisterFunctions}}
    {{RegisterSubs}}
    return ret;
}

bool rpc_{{ServiceName}}_server::testConnection(std::string function, bson::bo _response, r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection)
{
    return true;
}

bson::bo rpc_{{ServiceName}}_server::do_onConnected( const bson::bo &param, const r_int64 seq, const boost::shared_ptr<net::NetConnection> &pConnection )
{
    onConnected(pConnection);
    return bson::bo();
}

bson::bo rpc_{{ServiceName}}_server::do_onError( const bson::bo &param, const r_int64 seq, const boost::shared_ptr<net::NetConnection> &pConnection )
{
    onError(pConnection);
    return bson::bo();
}

{{FunctionContent}}

{{PushFunctionContent}}

{{SubFunctionContent}}\
'''

SERVER_FUNCTION_TEMPLATE_CPP =\
u'''\
bson::bo rpc_{{ServiceName}}_server::_{{FuncName}}(const bson::bo &_response, const r_int64 _seq, const boost::shared_ptr<net::NetConnection> &_connection)
{
    if (testConnection("{{FuncName}}", _response, _seq , _connection))
    {
        net::RPCEngine::instance()->trafficWatch()->watch("request {{FuncName}}", _response.objsize());
        bson::bo _ret;
        {{InParamDeclear}}
        {{ParseBson}}
        {{OutParamDeclear}}
        if ({{FuncName}}({{InParamNames}} {{OutParamNames}} _seq, _connection))
        {
            ByteArray _bytes;
            net::NetPackageAlloc _alloc(_bytes);
            bson::BufBuilder bBuilder(512, _alloc);
            bson::bob _globalBuilder(bBuilder);
            _globalBuilder.append("status", net::STATUS_OK);
            bson::bob _builder(_globalBuilder.subobjStart("params"));
            {{GenBson}}
            _builder.done();
            bson::bo _response = _globalBuilder.done();
            int _size = 0;
            int _compress = COMPRESS_NONE;
            if (_connection->m_compressType == COMPRESS_DOUBLE_ZLIB)
            {
                _compress = COMPRESS_DOUBLE_ZLIB;
            }
            else if (_connection->m_compressType == COMPRESS_DOUBLE_LZMA)
            {
                _compress = COMPRESS_DOUBLE_LZMA;
            }
            _bytes = _alloc.makeRequest(_seq, NET_CMD_RPC, _compress, _size);
            _connection->sendData(_bytes, _size);
            net::RPCEngine::instance()->trafficWatch()->watch("{{FuncName}}", _size);
        }
        return _ret;
    } else {
        throw bson::bob().append("error", "not logined").obj();
    }
};

void rpc_{{ServiceName}}_server::send_{{FuncName}}({{SendOutParam}} bson::bo _error, r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection, r_uint8 compress /*= COMPRESS_NONE*/)
{
    ByteArray _bytes;
    net::NetPackageAlloc _alloc(_bytes);
    bson::BufBuilder bBuilder(512, _alloc);
    bson::bob _globalBuilder(bBuilder);
    if (_error.isEmpty())
    {
        _globalBuilder.append("status", net::STATUS_OK);
        bson::bob _builder(_globalBuilder.subobjStart("params"));
        {{GenBson}}
        _builder.done();
    } else {
        _globalBuilder.append("status", net::STATUS_ERROR);
        utils::appendToBuilder(_globalBuilder,"params", _error);
    }
    bson::bo _response =_globalBuilder.done();
    int _size = 0;
    int _compress = COMPRESS_NONE;
    if (_connection->m_compressType == COMPRESS_DOUBLE_ZLIB)
    {
        _compress = COMPRESS_DOUBLE_ZLIB;
    }
    else if (_connection->m_compressType == COMPRESS_DOUBLE_LZMA)
    {
        _compress = COMPRESS_DOUBLE_LZMA;
    }
    _bytes = _alloc.makeRequest(_seq, NET_CMD_RPC, _compress, _size);
    _connection->sendData(_bytes, _size);
    net::RPCEngine::instance()->trafficWatch()->watch("checkOrder", _size);
}
'''

SERVER_PUSH_FUNCTION_TEMPLATE_CPP =\
u'''\
void rpc_{{ServiceName}}_server::push_{{FuncName}}({{Params1}} const boost::shared_ptr<net::NetConnection> &_connection, r_uint8 compress /*= COMPRESS_NONE*/)
{
    ByteArray _bytes;
    net::NetPackageAlloc _alloc(_bytes);
    bson::BufBuilder _bBuilder(512, _alloc);
    bson::bob _globalBuilder(_bBuilder);
    _globalBuilder.append("method", "{{FuncName}}");
    bson::bob _builder(_globalBuilder.subobjStart("params"));
    {{GenBson}};
    _builder.done();
    bson::bo _obj = _globalBuilder.done();

    int _size = 0;
    _bytes = _alloc.makeRequest(0, NET_CMD_NOTIFICATON, COMPRESS_ZLIB, _size);
    if (_connection)
        _connection->sendData(_bytes, _size);
    net::RPCEngine::instance()->trafficWatch()->watch("pushProductNetValue", _size);
};

void rpc_{{ServiceName}}_server::pushAll_{{FuncName}}({{Params2}})
{
    ByteArray _bytes;
    net::NetPackageAlloc _alloc(_bytes);
    bson::BufBuilder _bBuilder(512, _alloc);
    bson::bob _globalBuilder(_bBuilder);
    _globalBuilder.append("method", "{{FuncName}}");
    bson::bob _builder(_globalBuilder.subobjStart("params"));
    {{GenBson}}
    _builder.done();
    bson::bo _obj = _globalBuilder.done();

    int _size = 0;
    _bytes = _alloc.makeRequest(0, NET_CMD_NOTIFICATON, COMPRESS_ZLIB, _size);
    if (m_server)
        m_server->sendDataToClients(_bytes, _size);
    net::RPCEngine::instance()->trafficWatch()->watch("pushProductNetValue", _size);
};
'''

SERVER_SUB_FUNCTION_TEMPLATE_CPP =\
u'''\
bson::bo rpc_{{ServiceName}}_server::_{{FuncName}}(const bson::bo &_response, const r_int64 _seq, const boost::shared_ptr<net::NetConnection> &_connection)
{
    if (testConnection("{{FuncName}}", _response, _seq , _connection))
    {
        bson::bo _ret;
        {{InParamDeclear}}
        {{ParseBson}}
        {{OutParamDeclear}}
        int nSubType = -1;
        if ({{FuncName}}({{InParamNames}} {{OutParamNames}} _seq, _connection))
        {
            bson::bob _builder;
            {{GenBson}}
            _ret = _builder.obj();
            net::RPCEngine::instance()->trafficWatch()->watch("{{FuncName}}", _ret.objsize());
        }
        return _ret;
    } else {
        throw bson::bob().append("error", "not logined").obj();
    }
};

bson::bo rpc_{{ServiceName}}_server::_{{FuncName}}_unsub(const bson::bo &_response, const r_int64 _seq, const boost::shared_ptr<net::NetConnection> &_connection)
{
    if (testConnection("{{FuncName}}_unsub", _response, _seq , _connection))
    {
        bson::bo _ret;
        {{InParamDeclear}}
        {{ParseBson}}
        bool _success = false;
        if ({{FuncName}}_unsub({{InParamNames}} _success, _seq, _connection))
        {
            bson::bob _builder;
            _builder.append("success", _success);
            _ret = _builder.obj();
            net::RPCEngine::instance()->trafficWatch()->watch("{{FuncName}}_unsub", _ret.objsize());
        }
        return _ret;
    } else {
        throw bson::bob().append("error", "not logined").obj();
    }
};

void rpc_{{ServiceName}}_server::send_{{FuncName}}({{SendOutParam}} r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection, r_uint8 compress /*= COMPRESS_NONE*/)
{
    bson::bob _builder;
    {{GenBson}}
    bson::bo response = _builder.obj();

    net::RPCServer::sendData(response, _seq, _connection, net::STATUS_OK, compress);
    net::RPCEngine::instance()->trafficWatch()->watch("{{FuncName}}", response.objsize());
}

void rpc_{{ServiceName}}_server::send_{{FuncName}}_unsub(bool success, r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection)
{
    bson::bob _builder;
    _builder.append("success", success);
    bson::bo response = _builder.obj();

    net::RPCServer::sendData(response, _seq, _connection);
    net::RPCEngine::instance()->trafficWatch()->watch("{{FuncName}}_unsub", response.objsize());
}
'''

VIRTUAL_FUNCTION_TEMPLATE = '''\
virtual bool {{FuncName}}({{InOutParam}} r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection){return false;};\
'''

VIRTUAL_SUB_FUNCTION_TEMPLATE = '''\
virtual bool {{FuncName}}({{InOutParam}} r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection){return false;};
virtual bool {{FuncName}}_unsub({{InParam}} bool& _success, r_int64 _seq, boost::shared_ptr<net::NetConnection> _connection){return false;};\
'''
