angular.module('app.utils.directives').directive('historyList', HistoryListDirective);

HistoryListDirective.$inject = ['$filter', '$http', '$uibModal', '$q', '$state', 'EmailAccount',
    'Note', 'NoteDetail', 'Case', 'DealDetail', 'EmailDetail', 'User', 'HLGravatar'];
function HistoryListDirective($filter, $http, $uibModal, $q, $state, EmailAccount,
                              Note, NoteDetail, Case, DealDetail, EmailDetail, User, HLGravatar) {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            target: '=',
            object: '=',
            dateStart: '=?',
            dateEnd: '=?',
            parentObject: '=?',
        },
        templateUrl: 'utils/directives/historylist.html',
        link: function(scope, element, attrs) {
            var noteTargets = ['account', 'contact', 'deal', 'case'];
            var caseTargets = ['account', 'contact'];
            var dealTargets = ['account'];
            var emailTargets = ['account', 'contact'];
            var page = 0;
            var pageSize = 50;

            scope.history = {};
            scope.history.list = [];
            scope.history.types = {
                '': {name: 'All', visible: true},
                'note': {name: 'Notes', visible: false},
                'case': {name: 'Cases', visible: false},
                'deal': {name: 'Deals', visible: false},
                'email': {name: 'Emails', visible: false},
            };
            scope.history.activeFilter = '';
            scope.history.showMoreText = 'Show more';
            scope.history.loadMore = loadMore;
            scope.history.reloadHistory = reloadHistory;
            scope.history.addNote = addNote;
            scope.history.editNote = editNote;
            scope.history.pinNote = pinNote;
            scope.history.deleteNote = deleteNote;
            scope.history.filterType = filterType;

            scope.note = {};
            scope.note.type = 0;

            activate();

            ////////

            function activate() {
                // Somehow calling autosize on page content load does not work
                // in the historylist.
                autosize($('textarea'));
                loadMore();
            }

            function filterType(value) {
                var key;
                var selectedCount;

                scope.history.activeFilter = value;
                // Loop through the months to hide the monthname when there
                // aren't any items in that month that are shown due to
                // the filter that is being selected.
                for (key in scope.history.list.nonPinned) {
                    selectedCount = $filter('filter')(scope.history.list.nonPinned[key].items, {historyType: value}).length;
                    scope.history.list.nonPinned[key].isVisible = !!selectedCount;
                }
            }

            function loadMore() {
                if (!scope.object.$resolved) {
                    scope.object.$promise.then(function(obj) {
                        _fetchHistory(obj);
                    });
                } else {
                    _fetchHistory(scope.object);
                }
            }

            function reloadHistory() {
                page -= 1;
                loadMore();
            }

            function _fetchHistory(obj) {
                var history = [];
                var promises = [];
                var neededLength = (page + 1) * pageSize;
                var requestLength = neededLength + 1;
                var notePromise;
                var filterquery;
                var i;
                var dateFilteredList;

                page += 1;

                // Check if we need to fetch notes
                if (noteTargets.indexOf(scope.target) !== -1) {
                    if (scope.target === 'account' && obj.contact && obj.contact.length) {
                        filterquery = '(content_type:' + scope.target + ' AND object_id:' + obj.id + ')';

                        // Show all notes of contacts linked to the account
                        for (i = 0; i < obj.contact.length; i++) {
                            filterquery += ' OR (content_type:contact AND object_id:' + obj.contact[i] + ')';
                        }

                        notePromise = NoteDetail.query({filterquery: filterquery, size: requestLength}).$promise;
                    } else {
                        notePromise = NoteDetail.query({filterquery: 'content_type:' + scope.target + ' AND object_id:' + obj.id, size: requestLength}).$promise;
                    }

                    promises.push(notePromise);  // Add promise to list of all promises for later handling

                    notePromise.then(function(results) {
                        results.forEach(function(note) {
                            // Get user for notes to show profile picture correctly.
                            User.get({id: note.author.id}, function(userObject) {
                                note.author = userObject;
                            });

                            // Set notes shown property to true to have toggled open
                            // as default.
                            if (note.is_pinned) {
                                note.shown = true;
                            }

                            // If it's a contact's note, add extra attribute to the note
                            // so we can identify it in the template
                            if (scope.target === 'account' && note.content_type === 'contact') {
                                note.showContact = true;
                            }

                            history.push(note);
                        });
                    });
                }

                // Check if we need to fetch cases
                if (caseTargets.indexOf(scope.target) !== -1) {
                    var casePromise = Case.query({filterquery: scope.target + ':' + obj.id, size: 100}).$promise;
                    promises.push(casePromise);  // Add promise to list of all promises for later handling

                    casePromise.then(function(response) {
                        response.objects.forEach(function(caseItem) {
                            // Get user object for the assigned to user.
                            User.get({id: caseItem.assigned_to_id}, function(userObject) {
                                caseItem.assigned_to = userObject;
                            });

                            // Get user object for the created by user.
                            User.get({id: caseItem.created_by.id}, function(userObject) {
                                caseItem.created_by = userObject;
                            });

                            caseItem.historyType = 'case';

                            history.push(caseItem);
                            NoteDetail.query({filterquery: 'content_type:case AND object_id:' + caseItem.id, size: 15})
                                .$promise.then(function(notes) {
                                    angular.forEach(notes, function(note) {
                                        // Get user for notes to show profile picture correctly.
                                        User.get({id: note.author.id}, function(author) {
                                            note.author = author;
                                        });
                                    });

                                    caseItem.notes = notes;
                                });
                        });
                    });
                }

                // Check if we need to fetch deals
                if (dealTargets.indexOf(scope.target) !== -1) {
                    var dealPromise = DealDetail.query({filterquery: scope.target + ':' + obj.id, size: requestLength}).$promise;
                    promises.push(dealPromise);  // Add promise to list of all promises for later handling

                    dealPromise.then(function(results) {
                        results.forEach(function(deal) {
                            // Get user object for the assigned to user.
                            User.get({id: deal.assigned_to_id}, function(userObject) {
                                deal.assigned_to = userObject;
                            });

                            // Get user object to show profile picture correctly.
                            User.get({id: deal.created_by.id}, function(userObject) {
                                deal.created_by = userObject;
                            });

                            NoteDetail.query({
                                filterquery: 'content_type:deal AND object_id:' + deal.id,
                                size: 5,
                            }).$promise.then(function(notes) {
                                angular.forEach(notes, function(note) {
                                    // Get user for notes to show profile picture correctly.
                                    User.get({id: note.author.id}, function(author) {
                                        note.author = author;
                                    });
                                });
                                deal.notes = notes;
                            });
                            history.push(deal);
                        });
                    });
                }

                // Check if we need to fetch emails
                if (emailTargets.indexOf(scope.target) !== -1) {
                    var tenantEmailAccountPromise = EmailAccount.query().$promise;
                    promises.push(tenantEmailAccountPromise); // Add tenant email query to promises list

                    var emailPromise;
                    if (scope.target === 'account') {
                        emailPromise = EmailDetail.query({account_related: obj.id, size: requestLength}).$promise;
                    } else {
                        emailPromise = EmailDetail.query({contact_related: obj.id, size: requestLength}).$promise;
                    }
                    promises.push(emailPromise);  // Add promise to list of all promises for later handling

                    $q.all([tenantEmailAccountPromise, emailPromise]).then(function(results) {
                        var tenantEmailAccountList = results[0].results;
                        var emailMessageList = results[1];

                        emailMessageList.forEach(function(email) {
                            email.gravatar = HLGravatar.getGravatar(email.sender_email);

                            // Foldout email on default in the historylist.
                            email.shown = true;

                            tenantEmailAccountList.forEach(function(emailAddress) {
                                if (emailAddress.email_address === email.sender_email) {
                                    email.right = true;
                                }
                            });
                            history.push(email);
                        });
                    });
                }

                // Get all history types and add them to a common history.
                $q.all(promises).then(function() {
                    var orderedHistoryList = {pinned: [], nonPinned: {}, totalItems: history.length};

                    // To properly sort the history list we need to compare dates
                    // because email doesn't have the modified key we decided
                    // to add an extra key called historySortDate which the list
                    // uses to sort properly. We add the sent_date of email to the
                    // object, and the modified date for the other types.
                    for (i = 0; i < history.length; i++) {
                        if (history[i].historyType === 'email') {
                            history[i].historySortDate = history[i].sent_date;
                        } else {
                            history[i].historySortDate = history[i].modified;
                        }
                    }

                    if (scope.dateStart && scope.dateEnd) {
                        dateFilteredList = [];

                        for (i = 0; i < history.length; i++) {
                            if (moment(history[i].historySortDate).isBetween(scope.dateStart, scope.dateEnd)) {
                                dateFilteredList.push(history[i]);
                            }
                        }
                    }

                    if (dateFilteredList) {
                        history = dateFilteredList;
                    }

                    $filter('orderBy')(history, 'historySortDate', true).forEach(function(item) {
                        var date = '';
                        var key = '';

                        scope.history.types[item.historyType].visible = true;

                        if (item.is_pinned) {
                            orderedHistoryList.pinned.push(item);
                        } else {
                            // If it's an 'extra' history list we want to
                            // exclude the item that's being viewed.
                            if (!scope.parentObject || item.id !== scope.parentObject.id) {
                                if (item.hasOwnProperty('modified')) {
                                    date = item.modified;
                                } else {
                                    date = item.sent_date;
                                }

                                key = moment(date).year() + '-' + (moment(date).month() + 1);

                                if (!orderedHistoryList.nonPinned.hasOwnProperty(key)) {
                                    orderedHistoryList.nonPinned[key] = {isVisible: true, items: []};
                                }

                                orderedHistoryList.nonPinned[key].items.push(item);
                            } else {
                                orderedHistoryList.totalItems -= 1;
                            }
                        }
                    });

                    // Get first key in the nonPinned list to target the first
                    // item in the history items to set the property to shown.
                    for(var key in orderedHistoryList.nonPinned) break;
                    if (orderedHistoryList.nonPinned[key]) {
                        orderedHistoryList.nonPinned[key].items[0].shown = true;
                    }

                    scope.history.list = orderedHistoryList;
                });
            }

            function addNote(note) {
                $http({
                    method: 'POST',
                    url: '/notes/create/',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    data: $.param({
                        content: note.content,
                        type: note.type,
                        content_type: scope.target,
                        object_id: scope.object.id,
                    }),
                }).success(function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function editNote(note) {
                var modalInstance = $uibModal.open({
                    templateUrl: 'utils/controllers/note_edit.html',
                    controller: 'EditNoteModalController',
                    size: 'lg',
                    resolve: {
                        note: function() {
                            return note;
                        },
                    },
                });

                modalInstance.result.then(function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function pinNote(note, isPinned) {
                Note.update({id: note.id}, {is_pinned: isPinned}, function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }

            function deleteNote(note) {
                var month = moment(note.modified).format('M');
                var year = moment(note.modified).format('YYYY');
                var index;

                if (confirm('Are you sure?')) {
                    Note.delete({
                        id: note.id,
                    }, function() {  // On success
                        if (note.is_pinned) {
                            index = scope.history.list.pinned.indexOf(note);
                            scope.history.list.pinned.splice(index, 1);
                        } else {
                            index = scope.history.list.nonPinned[year + '-' + month].items.indexOf(note);
                            scope.history.list.nonPinned[year + '-' + month].items.splice(index, 1);
                        }
                    }, function(error) {  // On error
                        alert('something went wrong.');
                    });
                }
            }
        },
    };
}
