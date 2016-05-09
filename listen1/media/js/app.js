(function() {
  'use strict';

  Storage.prototype.setObject = function(key, value) {
      this.setItem(key, JSON.stringify(value));
  }

  Storage.prototype.getObject = function(key) {
      var value = this.getItem(key);
      return value && JSON.parse(value);
  }

  var app = angular.module('listenone', ['angularSoundManager', 'ui-notification']);

  app.config(function(NotificationProvider) {
    NotificationProvider.setOptions({
        delay: 2000,
        startTop: 20,
        startRight: 10,
        verticalSpacing: 20,
        horizontalSpacing: 20,
        positionX: 'center',
        positionY: 'top'
    });
  });

  // control main view of page, it can be called any place
  app.controller('NavigationController', ['$scope', '$http',
    '$httpParamSerializerJQLike', '$timeout',
    'angularPlayer', 'Notification', '$rootScope',
    function($scope, $http, $httpParamSerializerJQLike,
      $timeout, angularPlayer, Notification, $rootScope){
    $scope.window_url_stack = [];
    $scope.current_tag = 1;
    $scope.is_window_hidden = 1;
    $scope.is_dialog_hidden = 1;

    $scope.songs = [];
    $scope.current_list_id = -1;

    $scope.dialog_song = '';
    $scope.dialog_type = 0;
    $scope.dialog_title = '';

    $scope.isDoubanLogin = false;
    $scope.$on('isdoubanlogin:update', function(event, data) {
      $scope.isDoubanLogin = data;
    });

    // tag
    $scope.showTag = function(tag_id){
      $scope.current_tag = tag_id;
      $scope.is_window_hidden = 1;
      $scope.window_url_stack = [];
      $scope.closeWindow();
    };

    // playlist window
    $scope.resetWindow = function() {
      $scope.cover_img_url = '/static/images/loading.gif';
      $scope.playlist_title = '';
      $scope.songs = [];
    };

    $scope.showWindow = function(url){
      $scope.is_window_hidden = 0;
      $scope.resetWindow();

      $scope.window_url_stack.push(url);
      $http.get(url).success(function(data) {
          if (data.status == '0') {
            Notification.info(data.reason);  
            $scope.popWindow();
            return;
          }
          $scope.songs = data.tracks;
          $scope.cover_img_url = data.info.cover_img_url;
          $scope.playlist_title = data.info.title;
          $scope.list_id = data.info.id;
          $scope.is_mine = data.is_mine;
      });
    };

    $scope.closeWindow = function(){
      $scope.is_window_hidden = 1;
      $scope.resetWindow();
      $scope.window_url_stack = [];
    };

    $scope.popWindow = function() {
      $scope.window_url_stack.pop();
      if($scope.window_url_stack.length === 0) {
        $scope.closeWindow();
      }
      else {
        $scope.resetWindow();
        var url = $scope.window_url_stack[$scope.window_url_stack.length-1];
        $http.get(url).success(function(data) {
            $scope.songs = data.tracks;
            $scope.cover_img_url = data.info.cover_img_url;
            $scope.playlist_title = data.info.title;
        });
      }
    };

    $scope.showPlaylist = function(list_id) {
      var url = '/playlist?list_id=' + list_id;
      $scope.showWindow(url);
    };

    $scope.showArtist = function(artist_id) {
      var url = '/artist?artist_id=' + artist_id;
      $scope.showWindow(url);
    };

    $scope.showAlbum = function(album_id) {
      var url = '/album?album_id=' + album_id;
      $scope.showWindow(url);
    };

    $scope.directplaylist = function(list_id){
      var url = '/playlist?list_id=' + list_id;

      $http.get(url).success(function(data) {
          $scope.songs = data.tracks;
          $scope.current_list_id = list_id;

          $timeout(function(){
            // use timeout to avoid stil in digest error.
            angularPlayer.clearPlaylist(function(data) {
              //add songs to playlist
              angularPlayer.addTrackArray($scope.songs);
              //play first song
              var index = 0;
              if (angularPlayer.getShuffle()) {
                var max = $scope.songs.length - 1;
                var min = 0;
                index = Math.floor(Math.random() * (max - min + 1)) + min;
              }
              if(index < $scope.songs.length) angularPlayer.playTrack($scope.songs[index].id);
              
            });
          }, 0);
      });
    };

    $scope.showDialog = function(dialog_type, data) {
      $scope.is_dialog_hidden = 0;
      var dialogWidth = 480;
      var left = $(window).width()/2 - dialogWidth/2;
      $scope.myStyle = {'left':  left + 'px'};

      if (dialog_type == 0) {
        $scope.dialog_title = '添加到歌单';
        var url = '/show_myplaylist';
        $scope.dialog_song = data;
        $http.get(url).success(function(data) {
            $scope.myplaylist = data.result;
        });
      }

      if (dialog_type == 2) {
        $scope.dialog_title = '登录豆瓣';
        $scope.dialog_type = 2;
      }
    };

    $scope.chooseDialogOption = function(option_id) {
      var url = '/add_myplaylist';

      $http({
        url: url,
        method: 'POST',
        data: $httpParamSerializerJQLike({
          list_id: option_id,
          id: $scope.dialog_song.id,
          title: $scope.dialog_song.title,
          artist: $scope.dialog_song.artist,
          url: $scope.dialog_song.url,
          artist_id: $scope.dialog_song.artist_id,
          album: $scope.dialog_song.album,
          album_id: $scope.dialog_song.album_id,
          source: $scope.dialog_song.source,
          source_url: $scope.dialog_song.source_url
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).success(function() {
        Notification.success('添加到歌单成功');  
        $scope.closeDialog();
        // add to current playing list
        if (option_id == $scope.current_list_id) {
          angularPlayer.addTrack($scope.dialog_song);
        }
      });
    };

    $scope.newDialogOption = function() {
      $scope.dialog_type = 1;
    };

    $scope.cancelNewDialog = function() {
      $scope.dialog_type = 0;
    };

    $scope.createAndAddPlaylist = function() {
      var url = '/create_myplaylist';

      $http({
        url: url,
        method: 'POST',
        data: $httpParamSerializerJQLike({
          list_title: $scope.newlist_title,
          id: $scope.dialog_song.id,
          title: $scope.dialog_song.title,
          artist: $scope.dialog_song.artist,
          url: $scope.dialog_song.url,
          artist_id: $scope.dialog_song.artist_id,
          album: $scope.dialog_song.album,
          album_id: $scope.dialog_song.album_id,
          source: $scope.dialog_song.source,
          source_url: $scope.dialog_song.source_url
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).success(function() {
        $rootScope.$broadcast('myplaylist:update');
        Notification.success('添加到歌单成功');  
        $scope.closeDialog();
      });
    };

    $scope.removeSongFromPlaylist = function(song, list_id) {
      var url = '/remove_track_from_myplaylist';

      $http({
        url: url,
        method: 'POST',
        data: $httpParamSerializerJQLike({
          list_id: list_id,
          track_id: song.id
        }),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).success(function() {
        // remove song from songs
        var index = $scope.songs.indexOf(song);
        if (index > -1) {
          $scope.songs.splice(index, 1);
        }
        Notification.success('删除成功');  
      });
    }

    $scope.closeDialog = function() {
      $scope.is_dialog_hidden = 1;
      $scope.dialog_type = 0;
    };

    $scope.setCurrentList = function(list_id) {
      $scope.current_list_id = list_id;
    };

    $scope.$on('player:playlist', function(event, data) {
      localStorage.setObject('current-playing', data);
    });

    $scope.$on('track:id', function(event, data) {
      var current = localStorage.getObject('player-settings');
      current.nowplaying_track_id = data;
      localStorage.setObject('player-settings', current);
    });
  }]);


  app.controller('PlayController', ['$scope', '$timeout','$log',
    '$anchorScroll', '$location', 'angularPlayer', '$http',
    '$httpParamSerializerJQLike','$rootScope', 'Notification',
     function($scope, $timeout, $log, $anchorScroll, $location, angularPlayer,
      $http, $httpParamSerializerJQLike, $rootScope, Notification){
      $scope.menuHidden = true;

      $scope.settings = {"playmode": 0, "nowplaying_track_id": -1};

      $scope.loadLocalSettings = function() {
        var defaultSettings = {"playmode": 0, "nowplaying_track_id": -1}
        var localSettings = localStorage.getObject('player-settings');
        if (localSettings == null) {
          $scope.settings = {"playmode": 0, "nowplaying_track_id": -1};
          $scope.saveLocalSettings();
        }
        else {
          $scope.settings = localSettings;
        }
        // apply settings
        var shuffleSetting;
        if ($scope.settings.playmode == 1) {
          shuffleSetting = true;
        }
        else {
          shuffleSetting = false;
        }
        if (angularPlayer.getShuffle() != shuffleSetting) {
          angularPlayer.toggleShuffle();
        }
      }

      $scope.saveLocalSettings = function() {
        localStorage.setObject('player-settings', $scope.settings);
      }

      $scope.loadLocalCurrentPlaying = function() {
        var localSettings = localStorage.getObject('current-playing');
        if (localSettings == null) {
          return;
        }
        // apply local current playing;
        angularPlayer.addTrackArray(localSettings);
      }

      $scope.saveLocalCurrentPlaying = function() {
        localStorage.setObjct('current-playing', angularPlayer.playlist)
      }

      $scope.changePlaymode = function() {
        // loop: 0, shuffle: 1
        angularPlayer.toggleShuffle();
        if (angularPlayer.getShuffle()) {
          $scope.settings.playmode = 1;
        }
        else {
          $scope.settings.playmode = 0;
        }
        $scope.saveLocalSettings();
      };

      $scope.$on('angularPlayer:ready', function(event, data) {
        $log.debug('cleared, ok now add to playlist');
        if (angularPlayer.getRepeatStatus() == false) {
            angularPlayer.repeatToggle();
        }
        //add songs to playlist
        var localCurrentPlaying = localStorage.getObject('current-playing');
        if (localCurrentPlaying == null) {
          return;
        }
        angularPlayer.addTrackArray(localCurrentPlaying);
        
        var localPlayerSettings = localStorage.getObject('player-settings');
        if (localPlayerSettings == null) {
          return;
        }
        var track_id = localPlayerSettings.nowplaying_track_id;
        if (track_id != -1) {
          angularPlayer.playTrack(track_id);
        }
        else {
          angularPlayer.play();
        }
        // disable open and play feature
        angularPlayer.pause();
      });

      $scope.gotoAnchor = function(newHash) {
        if ($location.hash() !== newHash) {
          // set the $location.hash to `newHash` and
          // $anchorScroll will automatically scroll to it
          $location.hash(newHash);
          $anchorScroll();
        } else {
          // call $anchorScroll() explicitly,
          // since $location.hash hasn't changed
          $anchorScroll();
        }
      };

      $scope.togglePlaylist = function() {
        var anchor = "song" + angularPlayer.getCurrentTrack();
        $scope.menuHidden = !$scope.menuHidden;
        if (!$scope.menuHidden) {
          $scope.gotoAnchor(anchor);
        }
      };

      $scope.playmylist = function(list_id){
        $timeout(function(){
          angularPlayer.clearPlaylist(function(data) {
            //add songs to playlist
            angularPlayer.addTrackArray($scope.songs);
            var index = 0;
            if (angularPlayer.getShuffle()) {
              var max = $scope.songs.length - 1;
              var min = 0;
              index = Math.floor(Math.random() * (max - min + 1)) + min;
            }
            //play first song
            if(index < $scope.songs.length) angularPlayer.playTrack($scope.songs[index].id);
          });
        }, 0);
        $scope.setCurrentList(list_id);
      };

      $scope.removemylist = function(list_id){
        var url = '/remove_myplaylist';

        $http({
          url: url,
          method: 'POST',
          data: $httpParamSerializerJQLike({
            list_id: list_id,
          }),
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }).success(function() {
          $rootScope.$broadcast('myplaylist:update');
          $scope.closeWindow();
          Notification.success('删除成功');  
        });
      };

      $scope.clonelist = function(list_id){
        var url = '/clone_playlist';

        $http({
          url: url,
          method: 'POST',
          data: $httpParamSerializerJQLike({
            list_id: list_id,
          }),
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }).success(function() {
          $rootScope.$broadcast('myplaylist:update');
          $scope.closeWindow();
          Notification.success('收藏到我的歌单成功');  
        });
      };

      $scope.myProgress = 0;
      $scope.changingProgress = false;

      $rootScope.$on('track:progress', function(event, data) {
          if ($scope.changingProgress == false) {
            $scope.myProgress = data;
          }
      });

      $rootScope.$on('track:myprogress', function(event, data) {
        $scope.$apply(function() {
          // should use apply to force refresh ui
          $scope.myProgress = data;
        });
      });
  }]);

  app.controller('InstantSearchController', ['$scope', '$http', '$timeout', 'angularPlayer',
    function($scope, $http, $timeout, angularPlayer) {
      $scope.tab = 0;
      $scope.keywords = '';

      $scope.changeTab = function(newTab){
        $scope.tab = newTab;
        $scope.result = [];
        $http.get('/search?source='+ $scope.tab + '&keywords=' + $scope.keywords).success(function(data) {
            // update the textarea
            $scope.result = data.result; 
        });
      };

      $scope.isActiveTab = function(tab){
        return $scope.tab === tab;
      };

      $scope.$watch('keywords', function (tmpStr) {
        if (!tmpStr || tmpStr.length === 0){
          $scope.result = [];
          return 0;
        }
        // if searchStr is still the same..
        // go ahead and retrieve the data
        if (tmpStr === $scope.keywords)
        {
          $http.get('/search?source='+ $scope.tab + '&keywords=' + $scope.keywords).success(function(data) {
            // update the textarea
            $scope.result = data.result; 
          });
        }
      });
  }]);

  app.directive('errSrc', function() {
    // http://stackoverflow.com/questions/16310298/if-a-ngsrc-path-resolves-to-a-404-is-there-a-way-to-fallback-to-a-default
    return {
      link: function(scope, element, attrs) {
        element.bind('error', function() {
          if (attrs.src != attrs.errSrc) {
            attrs.$set('src', attrs.errSrc);
          }
        });
        attrs.$observe('ngSrc', function(value) {
          if (!value && attrs.errSrc) {
            attrs.$set('src', attrs.errSrc);
          }
        });
      }
    }
  });

  app.directive('resize', function ($window) {
    return function (scope, element) {
      var w = angular.element($window);
          var changeHeight = function(){
            var headerHeight = 90;
            var footerHeight = 90;
            element.css('height', (w.height() - headerHeight - footerHeight) + 'px' );
          };  
        w.bind('resize', function () {        
            changeHeight();   // when window size gets changed             
      });  
          changeHeight(); // when page loads          
    };
  });

  app.directive('addAndPlay', ['angularPlayer', function (angularPlayer) {
        return {
            restrict: "EA",
            scope: {
                song: "=addAndPlay"
            },
            link: function (scope, element, attrs) {
                element.bind('click', function (event) {
                    angularPlayer.addTrack(scope.song);
                    angularPlayer.playTrack(scope.song.id);
                });
            }
        };
    }]);

  app.directive('addWithoutPlay', ['angularPlayer', 'Notification',
    function (angularPlayer, Notification) {
        return {
            restrict: "EA",
            scope: {
                song: "=addWithoutPlay"
            },
            link: function (scope, element, attrs) {
                element.bind('click', function (event) {
                    angularPlayer.addTrack(scope.song);
                    Notification.success("已添加到当前播放歌单");
                });
            }
        };
    }]);

  app.directive('openSongSource', ['angularPlayer', '$window',
    function (angularPlayer, $window) {
      return {
          restrict: "EA",
          scope: {
              song: "=openSongSource"
          },
          link: function (scope, element, attrs) {
              element.bind('click', function (event) {
                $window.open(scope.song.source_url, '_blank');
              });
          }
      };
  }]);

  app.directive('draggable', ['angularPlayer', '$document', '$rootScope',
      function(angularPlayer, $document, $rootScope) {
    return function(scope, element, attr) {
      var x;
      var container; 

      element.on('mousedown', function(event) {
        scope.changingProgress = true;
        container = document.getElementById('progressbar').getBoundingClientRect();
        // Prevent default dragging of selected content
        event.preventDefault();
        x = event.clientX - container.left;
        setPosition();
        $document.on('mousemove', mousemove);
        $document.on('mouseup', mouseup);

      });

      function mousemove(event) {
        x = event.clientX - container.left;
        setPosition();
      }

      function changeProgress(progress) {
        if (angularPlayer.getCurrentTrack() === null) {
            return;
        }
        var sound = soundManager.getSoundById(angularPlayer.getCurrentTrack());
        var duration = sound.durationEstimate;
        sound.setPosition(progress * duration);
      }

      function setPosition() {
        if (container) {
          if (x < 0) {
            x = 0;
          } else if (x > container.right - container.left) {
            x = container.right - container.left;
          }
        }
        var progress = x / (container.right - container.left);
        $rootScope.$broadcast('track:myprogress', progress*100);
      }

      function mouseup() {
        var progress = x / (container.right - container.left);
        changeProgress(progress);
        $document.off('mousemove', mousemove);
        $document.off('mouseup', mouseup);
        scope.changingProgress = false;
      }
    };
  }]);

  app.controller('MyPlayListController', ['$http','$scope', '$timeout',  
        'angularPlayer', function($http, $scope, $timeout, angularPlayer){
    $scope.myplaylists = [];

    $scope.loadMyPlaylist = function(){
      $http.get('/show_myplaylist').success(function(data) {
        $scope.myplaylists = data.result;
      });
    };

    $scope.$watch('current_tag', function(newValue, oldValue) {
        if (newValue !== oldValue) {
          if (newValue == '1') {
            $scope.myplaylists = [];
            $scope.loadMyPlaylist();
          }
        }
    });
    $scope.$on('myplaylist:update', function(event, data) {
      $scope.loadMyPlaylist();
    });

  }]);

  app.controller('PlayListController', ['$http','$scope', '$timeout',  
        'angularPlayer', function($http, $scope, $timeout, angularPlayer){
    $scope.result = [];
    
    $scope.tab = 0;

    $scope.changeTab = function(newTab){
      $scope.tab = newTab;
      $scope.result = [];
      $http.get('/show_playlist?source=' + $scope.tab).success(function(data) {
        $scope.result = data.result;
      });
    };

    $scope.isActiveTab = function(tab){
      return $scope.tab === tab;
    };


    $scope.loadPlaylist = function(){
      $http.get('/show_playlist?source=' + $scope.tab).success(function(data) {
        $scope.result = data.result;
      });
    };
  }]);

  app.controller('ImportController', ['$http', 
    '$httpParamSerializerJQLike', '$scope', '$interval',
    '$timeout', '$rootScope', 'Notification', 'angularPlayer', 
    function($http, $httpParamSerializerJQLike, $scope,
      $interval, $timeout, $rootScope, Notification, angularPlayer){
    $scope.validcode_url = "";
    $scope.token = "";

    $scope.getLoginInfo = function(){
      $http.get('/dbvalidcode').success(function(data) {
        if (data.isLogin == 0) {
          $scope.validcode_url = data.captcha.path;
          $scope.token = data.captcha.token;
        }
        else {
          // already login
          $scope.isDoubanLogin = true;
          $rootScope.$broadcast('isdoubanlogin:update', true);
        }
      });
    };

    $scope.loginDouban = function(){
      $scope.session.token = $scope.token;
      $http({
        url: '/dblogin',
        method: 'POST',
        data: $httpParamSerializerJQLike($scope.session),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).success(function(data) {
        if (data.result.success == '1') {
          $scope.isDoubanLogin = true;
          $rootScope.$broadcast('isdoubanlogin:update', true);
          Notification.success("登录豆瓣成功");
        }
        else {
          $scope.validcode_url = data.result.path;
          $scope.token = data.result.token;
        }
      });
      $scope.session.solution = "";
    };

    $scope.logoutDouban = function() {
      $http({
        url: '/dblogout',
        method: 'GET'
      }).success(function(data) {
        $scope.isDoubanLogin = false;
        $rootScope.$broadcast('isdoubanlogin:update', false);
        Notification.success("退出登录豆瓣成功");
        $scope.getLoginInfo();
      });
    };

    $scope.importDoubanFav = function(){
      $http({
        url: '/dbfav',
        method: 'POST',
        data: $httpParamSerializerJQLike({command:'start'}),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).success(function(data) {
        $scope.status = '正在进行中：' + data.result.progress + '%';
        $scope.start();
      });
    };

    var promise;

    $scope.start = function() {
      // stops any running interval to avoid two intervals running at the same time
      $scope.stop(); 
      
      // store the interval promise
      promise = $interval(poll, 1000);
    };

    $scope.stop = function() {
      $interval.cancel(promise);
    };
    $scope.$on('$destroy', function() {
      $scope.stop();
    });

    function poll(){
      $http({
        url: '/dbfav',
        method: 'POST',
        data: $httpParamSerializerJQLike({command:'status'}),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }).success(function(data) {
        $scope.status = '正在进行中：' + data.result.progress + '%';
        if (data.result.progress == 100) {
          $scope.stop();
          $scope.status = '';
          Notification.success("红心兆赫已导入我的歌单");
        }
      });
    }
  }]);

})();
