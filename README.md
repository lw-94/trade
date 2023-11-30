# trade

py trade

## 获取

### 获取单币资金费率数据

``` sh
# symbol: BTC，ETH…… 默认获取所有币数据
python ./src/getFundingRate.py BTC
```

### 获取单币k线数据

``` sh
# symbol: BTC，ETH…… 默认获取所有币数据
python ./src/getKline.py BTC
```

## 生成单币回测data

``` sh
# symbol: BTC，ETH…… 默认BTC
# interval: xs，xh，xd，xw，xm，xy 默认全部时间
python ./src/trade.py ETH 1d
```

## 生成多币回测json

``` sh
# count: 随机count个币的回测，默认10
# interval: xs，xh，xd，xw，xm，xy 默认全部时间
python ./src/tradeMuti.py 5 1d
```
