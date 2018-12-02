var NewLine = function (api) {
    var newline = {
        version: "1.1",
        api: api,
        host: '127.0.0.1:8000',

        /*
        * 返回所有支持的判定条件列表
        * return: dict, 格式如下:
        * {
        *    {display-text}: {value},
        *    ....
        *    {display-text}: {value},
        * }
        * */
        get_all_supported_conditions: function (onsuccess, onerror) {
            var data = {
                path: '/conditions/all/'
            };
            return this.api.query(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 返回全部工步列表
        * return: dict, 格式参考 BXT12_NCT100_.steps文件：
        * **/
        get_steps: function (onsuccess, onerror) {
            var data = {
                path: '/steps/all/'
            };

            return this.api.query(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 返回指定名称的工步内容
        * return: dict, 格式参考 BXT12_NCT100_.steps文件中的step1-step4的格式
        * */
        get_single_step: function(name, onsuccess, onerror) {
            var data = {
                path: '/steps/single/',
                name: name
            };

            return this.api.query(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 保存工步
        * name: 工步名称，eg. step1, step2, step3....
        * step: dict 格式参考 BXT12_NCT100_.steps文件中的step1-step4的格式
        * **/
        step_save: function (name, step, onsuccess, onerror) {
            var data = {
                path: '/step/save/',
                name: name,
                data: step
            };

            return this.api.push(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 删除工步
        * name: 工步名称，eg. step1, step2, step3....
        * **/
        step_delete: function (name, onsuccess, onerror) {
            var data = {
                path: '/step/delete/',
                name: name,
            };

            return this.api.push(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 检查工步逻辑可用性
        * */
        steps_check: function (onsuccess, onerror) {
            var data = {
                path: '/step/check/',
            };

            return this.api.push(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 获取当前工步状态列表
        * */
        steps_status: function (onsuccess, onerror) {
            var data = {
                path: '/step/status/',
            };

            return this.api.push(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 启动工步逻辑
        * */
        steps_start: function (entry, onsuccess, onerror) {
            var data = {
                path: '/step/start/',
                entry: entry
            };

            return this.api.push(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 停止工步逻辑
        * */
        steps_stop: function (onsuccess, onerror) {
            var data = {
                path: '/step/stop/',
            };

            return this.api.push(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 暂停工步逻辑
        * 返回全部工步状态
        * */
        steps_pause: function (onsuccess, onerror) {
            var data = {
                path: '/step/pause/',
            };

            return this.api.push(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 恢复工步逻辑
        * 返回全部工步状态
        * */
        steps_resume: function (onsuccess, onerror) {
            var data = {
                path: '/step/resume/',
            };

            return this.api.push(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },

        /*
        * 重新启动工步逻辑
        * */
        steps_reboot: function (entry, onsuccess, onerror) {
            var data = {
                path: '/step/reboot/',
                entry: entry
            };

            return this.api.push(data).success(function (api, request, response) {
                if ( typeof onsuccess === "function" ) {
                    onsuccess(response.data)
                }
            }).error(function (api, request, response) {
                if ( typeof onerror === "function" ) {
                    onerror(response)
                }
            });
        },
    };
    return newline;
};
