# 服务器回程路由可视化
## 效果 [示例网站](https://t.elapse.cc)
![](https://cdn.nodeimage.com/i/4ZTJL0kOhxIWGGcPiCFSABV6uRCDJqSv.webp)
## 用法

```shell
cd NTraceWeb
chmod +x ntrace
pip install fastapi uvicorn gunicorn jinja2 python-multipart
gunicorn main:app -c gunicorn_conf.py
```
ip:8848 访问
## 其他说明
文件内的可执行文件ntrace，其实就是 [NTrace-core](https://github.com/nxtrace/NTrace-core) 稍微改了一点东西，使输出时可以带上经纬度，然后同步到下面的地图上，不放心可以自己编译。

将 NTrace-core/printer/realtime_printer.go 里面 157行后改成了下面的内容
```go
if net.ParseIP(ip).To4() != nil {
			fmt.Fprintf(color.Output, " %s %s %s %s %s (%s,%s)\n    %s   ",
				color.New(color.FgWhite, color.Bold).Sprintf("%s", res.Hops[ttl][i].Geo.Country),
				color.New(color.FgWhite, color.Bold).Sprintf("%s", res.Hops[ttl][i].Geo.Prov),
				color.New(color.FgWhite, color.Bold).Sprintf("%s", res.Hops[ttl][i].Geo.City),
				color.New(color.FgWhite, color.Bold).Sprintf("%s", res.Hops[ttl][i].Geo.District),
				fmt.Sprintf("%-6s", res.Hops[ttl][i].Geo.Owner),

				color.New(color.FgWhite, color.Bold).Sprintf("%.2f", res.Hops[ttl][i].Geo.Lat),
				color.New(color.FgWhite, color.Bold).Sprintf("%.2f", res.Hops[ttl][i].Geo.Lng),

				color.New(color.FgHiBlack, color.Bold).Sprintf("%-39s", res.Hops[ttl][i].Hostname),
			)
		} else {
			fmt.Fprintf(color.Output, " %s %s %s %s %s (%s,%s)\n    %s   ",
				color.New(color.FgWhite, color.Bold).Sprintf("%s", res.Hops[ttl][i].Geo.Country),
				color.New(color.FgWhite, color.Bold).Sprintf("%s", res.Hops[ttl][i].Geo.Prov),
				color.New(color.FgWhite, color.Bold).Sprintf("%s", res.Hops[ttl][i].Geo.City),
				color.New(color.FgWhite, color.Bold).Sprintf("%s", res.Hops[ttl][i].Geo.District),
				fmt.Sprintf("%-6s", res.Hops[ttl][i].Geo.Owner),
				
				color.New(color.FgWhite, color.Bold).Sprintf("%.2f", res.Hops[ttl][i].Geo.Lat),
				color.New(color.FgWhite, color.Bold).Sprintf("%.2f", res.Hops[ttl][i].Geo.Lng),

				color.New(color.FgHiBlack, color.Bold).Sprintf("%-32s", res.Hops[ttl][i].Hostname),
			)
		}
```