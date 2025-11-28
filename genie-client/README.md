# Genie Client API Service

## 安装

```bash
uv venv
source .venv/bin/activate # Linux/MacOS 执行
. .venv/Scripts/activate # Windows 执行
```

## API 文档

启动服务后，可以访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8188/docs
- ReDoc: http://localhost:8188/redoc

## API 端点

- `GET /health` - 健康检查
- `POST /v1/tool/list` - 工具列表(不支持分页)
- `POST /v1/tool/call` - 工具调用

## 示例请求

###  1、健康检查接口

```bash
curl "http://localhost:8188/health"
```

```json
{
  "status": "healthy",
  "timestamp": "2025-07-09T18:05:47.537919",
  "version": "0.1.0"
}
```

### 2、工具列表接口

```bash
curl -X POST 'http://localhost:8188/v1/tool/list' -H "Content-Type: application/json" -d '{
        "server_url": "https://mcp.amap.com/sse?key=xxxxxxxxxxxx"
}'
```

```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "name": "maps_direction_bicycling",
            "description": "骑行路径规划用于规划骑行通勤方案，规划时会考虑天桥、单行线、封路等情况。最大支持 500km 的骑行路线规划",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "出发点经纬度，坐标格式为：经度，纬度"
                    },
                    "destination": {
                        "type": "string",
                        "description": "目的地经纬度，坐标格式为：经度，纬度"
                    }
                },
                "required": [
                    "origin",
                    "destination"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_direction_driving",
            "description": "驾车路径规划 API 可以根据用户起终点经纬度坐标规划以小客车、轿车通勤出行的方案，并且返回通勤方案的数据。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "出发点经纬度，坐标格式为：经度，纬度"
                    },
                    "destination": {
                        "type": "string",
                        "description": "目的地经纬度，坐标格式为：经度，纬度"
                    }
                },
                "required": [
                    "origin",
                    "destination"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_direction_transit_integrated",
            "description": "根据用户起终点经纬度坐标规划综合各类公共（火车、公交、地铁）交通方式的通勤方案，并且返回通勤方案的数据，跨城场景下必须传起点城市与终点城市",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "出发点经纬度，坐标格式为：经度，纬度"
                    },
                    "destination": {
                        "type": "string",
                        "description": "目的地经纬度，坐标格式为：经度，纬度"
                    },
                    "city": {
                        "type": "string",
                        "description": "公共交通规划起点城市"
                    },
                    "cityd": {
                        "type": "string",
                        "description": "公共交通规划终点城市"
                    }
                },
                "required": [
                    "origin",
                    "destination",
                    "city",
                    "cityd"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_direction_walking",
            "description": "根据输入起点终点经纬度坐标规划100km 以内的步行通勤方案，并且返回通勤方案的数据",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "出发点经度，纬度，坐标格式为：经度，纬度"
                    },
                    "destination": {
                        "type": "string",
                        "description": "目的地经度，纬度，坐标格式为：经度，纬度"
                    }
                },
                "required": [
                    "origin",
                    "destination"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_distance",
            "description": "测量两个经纬度坐标之间的距离,支持驾车、步行以及球面距离测量",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "origins": {
                        "type": "string",
                        "description": "起点经度，纬度，可以传多个坐标，使用竖线隔离，比如120,30|120,31，坐标格式为：经度，纬度"
                    },
                    "destination": {
                        "type": "string",
                        "description": "终点经度，纬度，坐标格式为：经度，纬度"
                    },
                    "type": {
                        "type": "string",
                        "description": "距离测量类型,1代表驾车距离测量，0代表直线距离测量，3步行距离测量"
                    }
                },
                "required": [
                    "origins",
                    "destination"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_geo",
            "description": "将详细的结构化地址转换为经纬度坐标。支持对地标性名胜景区、建筑物名称解析为经纬度坐标",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "待解析的结构化地址信息"
                    },
                    "city": {
                        "type": "string",
                        "description": "指定查询的城市"
                    }
                },
                "required": [
                    "address"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_regeocode",
            "description": "将一个高德经纬度坐标转换为行政区划地址信息",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "经纬度"
                    }
                },
                "required": [
                    "location"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_ip_location",
            "description": "IP 定位根据用户输入的 IP 地址，定位 IP 的所在位置",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "ip": {
                        "type": "string",
                        "description": "IP地址"
                    }
                },
                "required": [
                    "ip"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_schema_personal_map",
            "description": "用于行程规划结果在高德地图展示。将行程规划位置点按照行程顺序填入lineList，返回结果为高德地图打开的URI链接，该结果不需总结，直接返回！",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "orgName": {
                        "type": "string",
                        "description": "行程规划地图小程序名称"
                    },
                    "lineList": {
                        "type": "array",
                        "description": "行程列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "行程名称描述（按行程顺序）"
                                },
                                "pointInfoList": {
                                    "type": "array",
                                    "description": "行程目标位置点描述",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "行程目标位置点名称"
                                            },
                                            "lon": {
                                                "type": "number",
                                                "description": "行程目标位置点经度"
                                            },
                                            "lat": {
                                                "type": "number",
                                                "description": "行程目标位置点纬度"
                                            },
                                            "poiId": {
                                                "type": "string",
                                                "description": "行程目标位置点POIID"
                                            }
                                        },
                                        "required": [
                                            "name",
                                            "lon",
                                            "lat",
                                            "poiId"
                                        ]
                                    }
                                }
                            },
                            "required": [
                                "title",
                                "pointInfoList"
                            ]
                        }
                    }
                },
                "required": [
                    "orgName",
                    "lineList"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_around_search",
            "description": "周边搜，根据用户传入关键词以及坐标location，搜索出radius半径范围的POI",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "location": {
                        "type": "string",
                        "description": "中心点经度纬度"
                    },
                    "radius": {
                        "type": "string",
                        "description": "搜索半径"
                    }
                },
                "required": [
                    "keywords",
                    "location"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_search_detail",
            "description": "查询关键词搜或者周边搜获取到的POI ID的详细信息",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "关键词搜或者周边搜获取到的POI ID"
                    }
                },
                "required": [
                    "id"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_text_search",
            "description": "关键字搜索 API 根据用户输入的关键字进行 POI 搜索，并返回相关的信息",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "查询关键字"
                    },
                    "city": {
                        "type": "string",
                        "description": "查询城市"
                    },
                    "citylimit": {
                        "type": "boolean",
                        "default": false,
                        "description": "是否限制城市范围内搜索，默认不限制"
                    }
                },
                "required": [
                    "keywords"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_schema_navi",
            "description": " Schema唤醒客户端-导航页面，用于根据用户输入终点信息，返回一个拼装好的客户端唤醒URI，用户点击该URI即可唤起对应的客户端APP。唤起客户端后，会自动跳转到导航页面。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "lon": {
                        "type": "string",
                        "description": "终点经度"
                    },
                    "lat": {
                        "type": "string",
                        "description": "终点纬度"
                    }
                },
                "required": [
                    "lon",
                    "lat"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_schema_take_taxi",
            "description": "根据用户输入的起点和终点信息，返回一个拼装好的客户端唤醒URI，直接唤起高德地图进行打车。直接展示生成的链接，不需要总结",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "slon": {
                        "type": "string",
                        "description": "起点经度"
                    },
                    "slat": {
                        "type": "string",
                        "description": "起点纬度"
                    },
                    "sname": {
                        "type": "string",
                        "description": "起点名称"
                    },
                    "dlon": {
                        "type": "string",
                        "description": "终点经度"
                    },
                    "dlat": {
                        "type": "string",
                        "description": "终点纬度"
                    },
                    "dname": {
                        "type": "string",
                        "description": "终点名称"
                    }
                },
                "required": [
                    "dlon",
                    "dlat",
                    "dname"
                ]
            },
            "annotations": null
        },
        {
            "name": "maps_weather",
            "description": "根据城市名称或者标准adcode查询指定城市的天气",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称或者adcode"
                    }
                },
                "required": [
                    "city"
                ]
            },
            "annotations": null
        }
    ]
}
```

### 3、工具调用接口

```bash
curl -X POST 'http://localhost:8188/call_tool' -H "Content-Type: application/json" -d '{
    "server_url": "https://mcp.amap.com/sse?key=xxxxxxxxxxxx",
    "name": "maps_geo",
    "arguments": {
        "address": "经海路地铁站"
    }
}'
```

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "_meta": null,
        "content": [
            {
                "type": "text",
                "text": "{\"results\":[{\"country\":\"中国\",\"province\":\"北京市\",\"city\":\"北京市\",\"citycode\":\"010\",\"district\":\"通州区\",\"street\":[],\"number\":[],\"adcode\":\"110112\",\"location\":\"116.562245,39.783587\",\"level\":\"公交地铁站点\"},{\"country\":\"中国\",\"province\":\"云南省\",\"city\":\"昆明市\",\"citycode\":\"0871\",\"district\":\"官渡区\",\"street\":\"经海路\",\"number\":[],\"adcode\":\"530111\",\"location\":\"102.768586,24.994150\",\"level\":\"道路\"},{\"country\":\"中国\",\"province\":\"云南省\",\"city\":\"昆明市\",\"citycode\":\"0871\",\"district\":\"官渡区\",\"street\":\"经海路\",\"number\":[],\"adcode\":\"530111\",\"location\":\"102.768585,24.994179\",\"level\":\"道路\"},{\"country\":\"中国\",\"province\":\"云南省\",\"city\":\"昆明市\",\"citycode\":\"0871\",\"district\":\"官渡区\",\"street\":\"经海路\",\"number\":[],\"adcode\":\"530111\",\"location\":\"102.768585,24.994179\",\"level\":\"道路\"}]}",
                "annotations": null
            }
        ],
        "isError": false
    }
}
```

