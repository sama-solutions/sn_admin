odoo.define('sn_admin.public', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');

/**
 * Widget pour la recherche AJAX en temps réel
 */
publicWidget.registry.SNAdminSearch = publicWidget.Widget.extend({
    selector: '.sn-admin-search',
    events: {
        'input .search-input': '_onSearchInput',
    },

    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        this.searchTimeout = null;
    },

    /**
     * Gestionnaire d'événement pour l'input de recherche
     * Debounce de 300ms pour éviter trop de requêtes
     */
    _onSearchInput: function (ev) {
        var self = this;
        var query = $(ev.currentTarget).val();

        // Clear previous timeout
        clearTimeout(this.searchTimeout);

        // Si la requête est trop courte, ne rien faire
        if (query.length < 3) {
            this._hideResults();
            return;
        }

        // Debounce: attendre 300ms avant de lancer la recherche
        this.searchTimeout = setTimeout(function () {
            self._performSearch(query);
        }, 300);
    },

    /**
     * Effectuer la recherche AJAX
     */
    _performSearch: function (query) {
        var self = this;

        ajax.jsonRpc('/organigramme/api/search', 'call', {
            q: query
        }).then(function (data) {
            self._displayResults(data.results);
        }).catch(function (error) {
            console.error('Search error:', error);
        });
    },

    /**
     * Afficher les résultats de recherche
     */
    _displayResults: function (results) {
        var $resultsContainer = this.$('.search-results');
        
        if (!$resultsContainer.length) {
            $resultsContainer = $('<div class="search-results list-group position-absolute w-100" style="z-index: 1000;"></div>');
            this.$('.search-input').after($resultsContainer);
        }

        $resultsContainer.empty();

        if (results.length === 0) {
            $resultsContainer.append('<div class="list-group-item">Aucun résultat trouvé</div>');
        } else {
            results.forEach(function (result) {
                var $item = $('<a class="list-group-item list-group-item-action" href="/organigramme/agent/' + result.id + '"></a>');
                $item.append('<h6 class="mb-1">' + result.name + '</h6>');
                $item.append('<p class="mb-1 small">' + result.function + '</p>');
                $item.append('<small class="text-muted">' + result.service + ' - ' + result.ministry + '</small>');
                $resultsContainer.append($item);
            });
        }

        $resultsContainer.show();
    },

    /**
     * Cacher les résultats
     */
    _hideResults: function () {
        this.$('.search-results').hide();
    },
});

/**
 * Widget pour les filtres dynamiques
 */
publicWidget.registry.SNAdminFilters = publicWidget.Widget.extend({
    selector: '.sn-admin-filters',
    events: {
        'change select[name="ministry_id"]': '_onMinistryChange',
        'change select[name="direction_id"]': '_onDirectionChange',
    },

    /**
     * Gestionnaire de changement de ministère
     * Filtre les directions selon le ministère sélectionné
     */
    _onMinistryChange: function (ev) {
        var ministryId = $(ev.currentTarget).val();
        var $directionSelect = this.$('select[name="direction_id"]');
        var $serviceSelect = this.$('select[name="service_id"]');

        if (!ministryId) {
            $directionSelect.find('option').show();
            $serviceSelect.find('option').show();
            return;
        }

        // Filtrer les directions
        $directionSelect.find('option').each(function () {
            var $option = $(this);
            var optionMinistryId = $option.data('ministry-id');
            
            if (!optionMinistryId || optionMinistryId == ministryId) {
                $option.show();
            } else {
                $option.hide();
            }
        });

        // Reset direction et service
        $directionSelect.val('');
        $serviceSelect.val('');
    },

    /**
     * Gestionnaire de changement de direction
     * Filtre les services selon la direction sélectionnée
     */
    _onDirectionChange: function (ev) {
        var directionId = $(ev.currentTarget).val();
        var $serviceSelect = this.$('select[name="service_id"]');

        if (!directionId) {
            $serviceSelect.find('option').show();
            return;
        }

        // Filtrer les services
        $serviceSelect.find('option').each(function () {
            var $option = $(this);
            var optionDirectionId = $option.data('direction-id');
            
            if (!optionDirectionId || optionDirectionId == directionId) {
                $option.show();
            } else {
                $option.hide();
            }
        });

        // Reset service
        $serviceSelect.val('');
    },
});

/**
 * Lazy loading des images
 */
publicWidget.registry.SNAdminLazyLoad = publicWidget.Widget.extend({
    selector: '.sn-admin-lazy-load',

    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        this._setupLazyLoad();
    },

    /**
     * Configuration du lazy loading avec Intersection Observer
     */
    _setupLazyLoad: function () {
        if ('IntersectionObserver' in window) {
            var lazyImages = document.querySelectorAll('img[data-src]');
            
            var imageObserver = new IntersectionObserver(function (entries, observer) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        var img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });

            lazyImages.forEach(function (img) {
                imageObserver.observe(img);
            });
        }
    },
});

/**
 * Gestion de la navigation au clavier
 */
$(document).ready(function () {
    // Améliorer l'accessibilité des cartes cliquables
    $('.card a').on('keypress', function (e) {
        if (e.which === 13) { // Enter key
            window.location.href = $(this).attr('href');
        }
    });

    // Fermer les résultats de recherche en cliquant à l'extérieur
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.sn-admin-search').length) {
            $('.search-results').hide();
        }
    });

    // Animation fade-in au scroll
    var fadeElements = $('.fade-in');
    if (fadeElements.length) {
        $(window).on('scroll', function () {
            fadeElements.each(function () {
                var elementTop = $(this).offset().top;
                var elementBottom = elementTop + $(this).outerHeight();
                var viewportTop = $(window).scrollTop();
                var viewportBottom = viewportTop + $(window).height();

                if (elementBottom > viewportTop && elementTop < viewportBottom) {
                    $(this).addClass('visible');
                }
            });
        });
    }
});

/**
 * Fonction de copie d'URL dans le presse-papier
 */
function copyToClipboard(url) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function() {
            showToast('URL copiée dans le presse-papier', 'success');
        }).catch(function(err) {
            console.error('Erreur lors de la copie:', err);
            showToast('Erreur lors de la copie', 'error');
        });
    } else {
        // Fallback pour les navigateurs anciens
        var textArea = document.createElement("textarea");
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('URL copiée dans le presse-papier', 'success');
        } catch (err) {
            showToast('Erreur lors de la copie', 'error');
        }
        document.body.removeChild(textArea);
    }
}

/**
 * Fonction de partage sur réseaux sociaux
 */
function shareOnSocialMedia(platform, url, title) {
    var shareUrls = {
        'facebook': 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url),
        'twitter': 'https://twitter.com/intent/tweet?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(title),
        'whatsapp': 'https://wa.me/?text=' + encodeURIComponent(title + ' ' + url),
        'linkedin': 'https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(url)
    };
    
    if (shareUrls[platform]) {
        window.open(shareUrls[platform], '_blank', 'width=600,height=400');
    }
}

/**
 * Fonction de téléchargement du QR code
 */
function downloadQRCode(model, id, name) {
    var url = '/organigramme/qrcode/' + model + '/' + id;
    var link = document.createElement('a');
    link.href = url;
    link.download = 'qrcode_' + name + '.png';
    link.click();
}

/**
 * Fonction d'affichage de toast (notifications)
 */
function showToast(message, type) {
    var toast = $('<div class="toast toast-' + type + '">' + message + '</div>');
    $('body').append(toast);
    setTimeout(function() {
        toast.fadeOut(function() {
            toast.remove();
        });
    }, 3000);
}

/**
 * Chargement de l'organigramme interactif
 */
function loadOrgChart(ministryId) {
    var container = $('#orgchart-container');
    if (!container.length) return;
    
    // Afficher le loader
    container.html('<div class="orgchart-loader"><div class="spinner-border" role="status"><span class="sr-only">Chargement...</span></div></div>');
    
    // Charger les données via AJAX
    $.ajax({
        url: '/organigramme/api/tree',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {ministry_id: ministryId}
        }),
        success: function(response) {
            if (response.result) {
                renderOrgChart(response.result);
            } else {
                container.html('<div class="orgchart-error"><i class="fa fa-exclamation-triangle"></i><p>Erreur lors du chargement de l\'organigramme</p></div>');
            }
        },
        error: function(error) {
            console.error('Erreur lors du chargement de l\'organigramme:', error);
            container.html('<div class="orgchart-error"><i class="fa fa-exclamation-triangle"></i><p>Erreur lors du chargement de l\'organigramme</p></div>');
        }
    });
}

/**
 * Afficher l'organigramme avec OrgChart.js
 */
function renderOrgChart(data) {
    var container = $('#orgchart-container');
    
    // Vérifier si OrgChart.js est chargé
    if (typeof $.fn.orgchart === 'undefined') {
        console.error("OrgChart.js n'est pas chargé");
        container.html('<div class="orgchart-error"><i class="fa fa-exclamation-triangle"></i><p>Bibliothèque OrgChart.js manquante</p></div>');
        return;
    }
    
    container.empty();
    
    // Initialiser OrgChart.js
    container.orgchart({
        data: data,
        nodeContent: 'title',
        pan: true,
        zoom: true,
        depth: 3,
        exportButton: true,
        exportFilename: 'organigramme_senegal'
    });
    
    // Gérer les clics sur les nœuds
    container.on('click', '.node', function() {
        var nodeId = $(this).data('node-id');
        var nodeType = $(this).data('node-type');
        if (nodeId && nodeType) {
            var modelName = nodeType.split('.')[1];
            window.location.href = '/organigramme/' + modelName + '/' + nodeId;
        }
    });
}

/**
 * Initialisation au chargement de la page
 */
$(document).ready(function() {
    // Boutons de partage
    $('.btn-share').on('click', function() {
        var platform = $(this).data('platform');
        var url = window.location.href;
        var title = $(this).data('title') || document.title;
        shareOnSocialMedia(platform, url, title);
    });
    
    // Bouton de copie d'URL
    $('.btn-copy-url').on('click', function() {
        var url = $(this).data('url') || window.location.href;
        copyToClipboard(url);
    });
    
    // Bouton de téléchargement QR code
    $('.btn-download-qr').on('click', function() {
        var model = $(this).data('model');
        var id = $(this).data('id');
        var name = $(this).data('name');
        downloadQRCode(model, id, name);
    });
    
    // Charger l'organigramme si on est sur la page /organigramme/tree
    if ($('#orgchart-container').length > 0) {
        var ministryId = $('#orgchart-container').data('ministry-id');
        loadOrgChart(ministryId);
    }
});

return {
    SNAdminSearch: publicWidget.registry.SNAdminSearch,
    SNAdminFilters: publicWidget.registry.SNAdminFilters,
    SNAdminLazyLoad: publicWidget.registry.SNAdminLazyLoad,
    copyToClipboard: copyToClipboard,
    shareOnSocialMedia: shareOnSocialMedia,
    downloadQRCode: downloadQRCode,
    showToast: showToast,
    loadOrgChart: loadOrgChart,
};

});
