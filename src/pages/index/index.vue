<template>
	<view class="container">
		<view class="bg-container">
			<image src="../../static/background.png" />
		</view>
		<input v-model="searchKeyword" type="text" placeholder="输入店铺名进行筛选" />
		<button type="primary" @tap="searchNearbyShops">搜索</button>
		<view v-if="shops.length > 0">
			<view v-for="(shop, index) in shops" :key="index" @tap="selectShop(shop)">
				<text>{{ shop.name }}</text>
			</view>
		</view>

		<view class="group-container">
			<p class="row_p">
				<view v-for="(row, rowIndex) in 2" :key="rowIndex" class="row">
					<view v-for="(item, idx) in getRowItems(rowIndex)" :key="idx" class="item">
						<view v-if="item.type == 'user'" @tap="selectItem(item)" class="user-item">
							<image class="avatar" :src="item.user.avatarUrl" mode="scaleToFill" />
							<text class="nickname">{{ item.user.nickName }}</text>
						</view>
						<view v-else class="empty-item">
							<image class="avatar" src="../../static/plus-sign.png" mode="scaleToFill" />
						</view>
					</view>
				</view>
			</p>
		</view>

		<view class="button-container">
			<button class="btn" type="primary" @tap="joinGroup">加入组团</button>
			<button class="btn" type="primary" @tap="joinGroup">退出组团</button>
		</view>
	</view>
</template>

<script>
import io from '@hyoga/uni-socket.io'
import './index.css'

export default {
	data() {
		return {
			serverUrl: 'http://localhost:8086',
			wsServerUrl: 'ws://localhost:8086',
			users: [],
			userInfo: null,
			searchKeyword: '',
			userLocation: null,
			shops: [] // 附近店铺列表
		};
	},
	computed: {
		getRowItems() {
			return rowIndex => {
				const start = rowIndex * 3;
				const end = start + 3;
				return this.displayItems.slice(start, end);
			}
		},
		displayItems() {
			const displayItems = [];
			const totalItems = 3 * 3;

			for (let i = 0; i < totalItems; i++) {
				if (i < this.users.length) {
					displayItems.push({ type: 'user', user: this.users[i] });
				} else {
					displayItems.push({ type: 'empty' })
				}
			}
			return displayItems
		}
	},
	methods: {
		getUsers() {
			uni.request({
				url: this.serverUrl + '/shop_users',
				method: 'GET',
				data: { shop: 's1' }
				, success: (res) => {
					if (res.statusCode === 200) {
						this.users = res.data
					} else {
						console.error('get users failed')
					}
				}, fail: (err) => {
					console.error('request failed.')
				}
			})
		},
		joinGroup() {
			this.getUserInfo().then(() => {
				uni.request({
					url: this.serverUrl + '/join_shop?shop=' + 's1',
					method: 'POST',
					data: {
						avatarUrl: this.userInfo.avatarUrl,
						nickName: this.userInfo.nickName
					},
					header: {
						'Content-Type': 'application/json'
					}
				});
			}).catch((err) => { console.log(err) })
		},

		showGroupSuccessModal() {
			uni.showModal({
				title: '组团成功',
				content: '快去收银台集结吧！',
				showCancel: false,
				confirmText: '收到',
				success: (res) => {
					// 弹窗关闭时触发的回调函数
					if (res.confirm) { }
				}
			})
		},
		getUserInfo() {
			return new Promise((resolve, reject) => {
				uni.getUserInfo({
					success: (res) => {
						this.userInfo = res.userInfo,
							resolve();
					},
					fail: (err) => {
						console.error("get user inf failed")
						reject(err)
					}
				})
			})
		},
		selectItem(item) {
			if (item.type == 'user') {
				console.log('choose', item.user.nickName)
			} else {
				console.log('run here')
			}
		},
		// 获取用户地理位置
		getUserLocation() {
			wx.getLocation({
				success: (res) => {
					this.userLocation = res;
				},
				fail: (res) => {
					console.error(res)
					console.error('获取用户地理位置失败');
				}
			});
		},
		connectWebsocket() {
			const socket = io(this.wsServerUrl, {
				transports: ['websocket', 'polling'],
			});
			socket.on('connect', () => {
				console.log('websocket connected.')

				socket.on('s1', (message) => {
					this.users = message

					// 超过3人即组队成功
					if (this.users.length >= 3) {
						this.showGroupSuccessModal()
					}
				})

				// socket.on('disconnect', () => {
				// 	console.log('websocket disconnected.')
				// 	socket.close();
				// })
			})
		},
		// 根据用户输入的关键词搜索附近的店铺
		searchNearbyShops() {
			if (!this.userLocation) {
				console.error("请先获取用户地理位置");
				return;
			}

			wx.request({
				url: 'https://apis.map.qq.com/ws/place/v1/search',
				data: {
					keyword: this.searchKeyword,
					boundary: `nearby(${this.userLocation.latitude},${this.userLocation.longitude},5000)`,
					key: 'YOUR_TENCENT_MAP_API_KEY',
					output: 'json'
				},
				success: (res) => {
					if (res.data.status === 0) {
						this.shops = res.data.data;
					} else {
						console.error('搜索附近店铺失败：', res.data.message);
					}
				},
				fail: (error) => {
					console.error('搜索附近店铺失败：', error);
				}
			})

			// 使用地图API根据关键词搜索附近的店铺，并更新this.shops
			// 比如：调用腾讯地图API
		},
		// 选中店铺
		selectShop(shop) {

			// 用户选中店铺后的操作，比如跳转到店铺详情页等
		}
	},
	mounted() {
		this.connectWebsocket();
		//   this.getUserLocation(); // 组件加载时获取用户地理位置
	},
	onLoad() {
		this.getUsers()
	}
};
</script>
