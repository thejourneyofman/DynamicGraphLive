/* utility */
var dynamicGraph = {};
var graph = {};
(function ($) {
    dynamicGraph.types = {
        create_random_graph: {
            required: ['dynamic_graph_n', 'dynamic_graph_e','dynamic_graph_l', 'dynamic_graph_k']
        },
        virus_screen_game: {
            required: ['dynamic_graph_n', 'dynamic_graph_e','dynamic_graph_p', 'dynamic_graph_x']
        }
    };

    dynamicGraph.mute = function (node) {
        if (!~node.getAttribute('class').search(/muted/))
            node.setAttributeNS(null, 'class', node.getAttribute('class') + ' muted');
    };

    dynamicGraph.unmute = function (node) {
        node.setAttributeNS(null, 'class', node.getAttribute('class').replace(/(\s|^)muted(\s|$)/g, '$2'));
    };

    dynamicGraph.plotGraph = function (svg, json) {
        console.log("json", json);
        if (json.result == 404) {
            alert(json.message);
            return true;
        };
        svg.graph.clear();
        var nodes = $.map(json.V, function (v, i) {
            node = {};
            node.id = v;
            node.label = 'Node ' + v;
            node.x = Math.random();
            node.y = Math.random();
            node.size = Math.random();
            node.color = '#666';
            svg.graph.addNode(node);
            return node;
        });

        var edges = $.map(json.E, function (e, i) {
            edge = {};
            edge.id = i;
            edge.source = e[0];
            edge.target = e[1];
            edge.size = Math.random();
            edge.color = '#ccc';
            svg.graph.addEdge(edge);
            return edge;
        });

        svg.refresh();

        $('.sigma-node').click(function() {
          // Muting
          $('.sigma-node, .sigma-edge').each(function() {
            dynamicGraph.mute(this);
          });
          // Unmuting neighbors
          var neighbors = svg.graph.neighborhood($(this).attr('data-node-id'));
          neighbors.nodes.forEach(function(node) {
            dynamicGraph.unmute($('[data-node-id="' + node.id + '"]')[0]);
          });
          neighbors.edges.forEach(function(edge) {
            dynamicGraph.unmute($('[data-edge-id="' + edge.id + '"]')[0]);
          });
        });
    };

})(jQuery);

/* main */
jQuery(function ($) {
    // Instantiate sigma:
    var svg = new sigma({
      graph: dynamicGraph,
      settings: {
        enableHovering: false
      }
    });

    svg.addRenderer({
      id: 'main',
      type: 'svg',
      container: document.getElementById('graph-container'),
      freeStyle: true
    });

    svg.bind('clickStage', function() {
          $('.sigma-node, .sigma-edge').each(function() {
               dynamicGraph.unmute(this);
          });
    });

    $('#graph-params-form').submit(function () {

        $('.progress').css('display', 'block');
        event.preventDefault();

        var typeName = $graphTypeInput.val(),
            type = dynamicGraph.types[typeName],
            data = {}

        $.each(type["required"], function (i, id) {
            var $input = $("#" + id);
            data[$input.attr('name')] = $input.val();
        });

        $.ajax({
            url:"/generate",
            type:"POST",
            cache: false,
            data:JSON.stringify(data),
            contentType:"application/json; charset=utf-8",
            dataType:"json",
            success: function (json) {
                dynamicGraph.plotGraph(svg, json);
                graph = json;
            },
            error: function (xhr, textStatus, errorThrown) {
                var json = $.parseJSON(xhr.responseText);
                var errors = json.errors;
            },
            complete: function () {
            }
        });
        return false;
    });

     $('#add-button').click(function () {

        var typeName = $graphTypeInput.val(),
            type = dynamicGraph.types[typeName],
            data = {}

        $.each(type["required"], function (i, id) {
            var $input = $("#" + id);
            data[$input.attr('name')] = $input.val();
        });
        data['graph'] = graph;

        $.ajax({
            url:"/add",
            type:"POST",
            cache: false,
            data:JSON.stringify(data),
            contentType:"application/json; charset=utf-8",
            dataType:"json",
            success: function (json) {
                dynamicGraph.plotGraph(svg, json);
                graph = json;
            },
            error: function (xhr, textStatus, errorThrown) {
                var json = $.parseJSON(xhr.responseText);
                var errors = json.errors;
            },
            complete: function () {
            }
        });
        return false;
    });

    $('#del-button').click(function () {

        var typeName = $graphTypeInput.val(),
            type = dynamicGraph.types[typeName],
            data = {}

        $.each(type["required"], function (i, id) {
            var $input = $("#" + id);
            data[$input.attr('name')] = $input.val();
        });
        data['graph'] = graph;

        $.ajax({
            url:"/delete",
            type:"POST",
            cache: false,
            data:JSON.stringify(data),
            contentType:"application/json; charset=utf-8",
            dataType:"json",
            success: function (json) {
                dynamicGraph.plotGraph(svg, json);
                graph = json;
            },
            error: function (xhr, textStatus, errorThrown) {
                var json = $.parseJSON(xhr.responseText);
                var errors = json.errors;
            },
            complete: function () {
            }
        });
        return false;
    });

    var $graphTypeInput = $('#graph-type'),
        $params = $('#params > div'),
        $paramsInputs = $params.find('input');
        $('#graph-type').change(function () {
            var typeName = $graphTypeInput.val(),
                type = dynamicGraph.types[typeName];
            $paramsInputs.attr('disabled', 'disabled');
            $params.hide();
            $.each(type['required'], function (i, id) {
                var $input = $('#' + id);
                $input.parent().show();
                $input.removeAttr('disabled');
            });
        }).change();

});
