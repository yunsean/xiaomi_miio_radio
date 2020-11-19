**~~该插件已废弃，请使用https://github.com/yunsean/miio_acpartner~~**

## 小米空调伴侣广播控制 for home assistant

### 部署

将下载得到的radio目录，放到python的python的home assitant组件目录下，比如windows下的目录可能在：
C:\Users\Dylan\AppData\Local\Programs\Python\Python36\Lib\site-packages\homeassistant\components
（注意你安装python版本可能与此不同，建议通过搜索site-packages并定位到homeassistant\components下）

### 配置

在你的configuration.yaml文件中添加如下组件：

``` yaml
radio:
  - platform: xiaomi_miio
    host: YOUR_HOST
    token: YOUR_TOKEN
    name: "ChildrenRoom FM"  
```

token的获取方式与空调伴侣获取方式一致。

### 服务

提供如下服务：

#### radio.turn_on

  打开广播
  指定entity_id为打开指定空调伴侣的广播，不指定则打开所配置的所有radio组件对应的设备广播

#### radio.turn_off

  关闭广播
  指定entity_id为关闭指定空调伴侣的广播，不指定则关闭所配置的所有radio组件对应的设备广播

#### radio.toggle

  切换打开关闭状态
  entity_id用途与上述两个方式一致

#### radio.set_volume

  设置音量
  entity_id用途与上述两个方式一致
  volume为音量值0-100
  {
    "entity_id": "radio.childrenroom_fm",
    "volume": 100
  }

#### radio.play_next

  播放下一个收藏频道【当前只能在频道编号最低的10个频道中循环】
  entity_id用途与上述两个方式一致

#### radio.play_prev 

  播放上一个收藏频道【当前只能在频道编号最低的10个频道中循环】
  entity_id用途与上述两个方式一致   

#### radio.play_url

  播放指定频道
  entity_id用途与上述两个方式一致
  url为需要播放的频带ID（不是真正的网络地址哦）
  {
    "entity_id": "radio.childrenroom_fm",
    "url": 1739
  }
  目前没有找到如何直接播放一个网络地址的方法，通过add_channels添加进去的频道一直是空地址。。。
频道ID的获取方式：
  1、首先将你要播放的频道，通过米家APP加入到收藏里面，也就是通过空调伴侣的“网络收音机”进入后，在“我的收藏”中能够看到
  2、通过home assitant的states接口或者网站的states页面（左侧“开发者工具”下方有一对尖括号图标那个），找到你的设备，右侧中可以看到channels，后边有形如：
  "chs": [
    {
      "id": 751,
      "type": 0,
      "url": "http://live.xmcdn.com/live/751/64.m3u8"
    },
  其中id即为频道ID，可以通过属性查看到当前正在播放的频道ID【channel】。
  space_free: 11190211
  channel: 1065
  volume: 100

### 配置script

  参考：

``` yaml
  children_fm_music:
    sequence:
      - service: radio.play_url
        data_template:
          entity_id: radio.childrenroom_fm
          url: 1739
      - service: radio.set_volume
        data_template:
          entity_id: radio.childrenroom_fm
          volume: 75
```


理论上同时支持空调伴侣和小米网关（空调伴侣二代，圆坨坨那货，测试通过！）          
Enjoy it!          