/**
* Toggle the content of the given element, make the visible invisible and vice versa.
*/
(function($) {
    "use strict";

    var pluginName = 'toggleContent';

    var ContentToggle = function(el, options) {
        //Defaults:
        this.opts = $.extend({}, ContentToggle.defaults, options);

        // Make jquery objects of all elements
        this.$el= $(el);

        // Store a reference to this instance
        this.$el.data(pluginName, this);

        // Keep track of our status
        this.isToggled = false;

        // Set the elements we need to toggle
        this.setElements();

        // start listening for hovers:
        this.listen();
    };

    ContentToggle.defaults = {
        animateToggle: true,
        animationDuration: 600
    };

    ContentToggle.prototype.getAfterDimensions = function(el, inEl, outEl) {
        // Return the dimensions of our element after toggle, so we can animate.
        var $clone = $(el).clone(),
            $toggleIn,
            $toggleOut;

        $clone.css({
            'visibility': 'hidden',
            'width': '',
            'heigth': '',
            'maxWidth': '',
            'maxHeight': ''
        });

        $clone.empty();

        $toggleIn = $(inEl).clone();
        $toggleOut = $(outEl).clone();

        $clone.append($toggleIn);
        $clone.append($toggleOut);

        $toggleIn.show();
        $toggleOut.hide();

        $(el).parent().append($clone);

        var width = $clone.outerWidth(),
            height = $clone.outerHeight();

        $clone.remove();

        return {w:width, h:height};
    };

    ContentToggle.prototype.doToggle = function(useAnimation, duration) {
        var self = this,
            $toggleIn,
            $toggleOut;

        // Set the elements in the order we want to toggle them
        // and set the isToggled var to the oposite value for the next call
        if (!self.isToggled) {
            $toggleIn = self.$toggleFirst;
            $toggleOut = self.$toggleSecond;
            self.isToggled = true;
        } else {
            $toggleIn = self.$toggleSecond;
            $toggleOut = self.$toggleFirst;
            self.isToggled = false;
        }

        var afterDimensions = this.getAfterDimensions(self.$el, $toggleIn, $toggleOut),
            afterWidth = afterDimensions['w'],
            afterHeight = afterDimensions['h'];

        self.$el.css('height', afterHeight);

        if (useAnimation) {
            self.$el.stop().animate({
                width: afterWidth
            }, duration);

            $toggleOut.stop().slideUp(duration/2, function() {
                $toggleIn.stop().slideDown(duration/2, function() {
                    self.$el.css('height', '');
                    self.$el.css('width', '');
                });
            });
        } else {
            self.$el.css('width', afterWidth);

            $toggleIn.show();
            $toggleOut.hide();

            self.$el.css('height', '');
            self.$el.css('width', '');
        }
    };

    ContentToggle.prototype.setElements = function() {
        this.$toggleFirst = this.$el.children(':hidden');
        this.$toggleSecond = this.$el.children(':visible');
    };

    ContentToggle.prototype.listen = function() {
        var self = this;

        this.$el.on('mouseenter mouseleave', function() {
            self.doToggle(self.opts.animateToggle, self.opts.animationDuration);
        });
    };

    ContentToggle.toggle = function(el, options) {
        // Because we are not in the prototype space, get the self manually
        var self = ContentToggle.getOrCreate(el),
            animateToggle = (options && 'animateToggle' in options) ? options.animateToggle : self.opts.animateToggle,
            animationDuration = (options && 'animationDuration' in options) ? options.animationDuration : self.opts.animationDuration;

        self.doToggle(animateToggle, animationDuration);

        return self.$el
    };

    ContentToggle.refresh = function(el) {
        // Because we are not in the prototype space, get the self manually
        var self = ContentToggle.getOrCreate(el);
        self.setElements();
        return self.$el
    };

    ContentToggle.getOrCreate = function(el, options) {
        var rev = $(el).data(pluginName);

        if (!rev) {
            rev = new ContentToggle(el, options);
        }

        return rev;
    };

    $.fn[pluginName] = function() {
        var options, fn, args;
        // Create a new Formset for each element
        if (arguments.length === 0 || (arguments.length === 1 && $.type(arguments[0]) != 'string')) {
            options = arguments[0];
            return this.each(function() {
                return ContentToggle.getOrCreate(this, options);
            });
        }

        // Call a function on each element in the selector
        fn = arguments[0];
        args = $.makeArray(arguments).slice(1);

        if (fn in ContentToggle) {
            // Call the class method if it exists
            args.unshift(this);
            return ContentToggle[fn].apply(ContentToggle, args);
        } else {
            throw new Error("Unknown function call " + fn + " for $.fn." + pluginName);
        }
    };

    // Initialize content toggler for default selector
    $('.toggle-content')[pluginName]();
})(jQuery);
