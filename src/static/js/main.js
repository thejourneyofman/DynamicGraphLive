/* utility */
var dynamicGraph = {};
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

    dynamicGraph.request = function (svg, action_type, nodes_number) {

        if (!!window.EventSource && action_type == "new") {
          var source = new EventSource("/api/" + action_type + "/" + nodes_number);
        }

        if (!!window.EventSource && action_type == "add") {
          var source = new EventSource("/api/" + action_type + "/" + nodes_number);
        }

        source.addEventListener('message', function(e) {
          json  = JSON.parse(e.data);
          dynamicGraph.plotGraph(svg, json);

          if (Number(e.lastEventId) >= nodes_number ) {
             dynamicGraph.show_alert(`Generation Complete.`, "success");
             source.close(); // stop retry
          }
          // Get the loaded amount and total filesize (bytes)
          var loaded = Number(e.lastEventId);
          var total = nodes_number;
          // Calculate percent completed
          var percent_complete = (loaded / total) * 100;
          // Update the progress text and progress bar
          progress.setAttribute("style", `width: ${Math.floor(percent_complete)}%`);
          progress_status.innerText = `${Math.floor(percent_complete)}% completed`;

        }, false);

        // error handler
        source.addEventListener("error", function (e) {
          dynamicGraph.reset();
          if (e.readyState == EventSource.CLOSED) {
            dynamicGraph.show_alert(`Error generating graph`, "warning");
          }
        }, false);

        // abort handler
        cancel_btn.addEventListener("click", function (e) {
           dynamicGraph.show_alert(`Generation cancelled`, "danger");
           dynamicGraph.reset();
           source.close();
        }, false);
    };

    dynamicGraph.plotGraph = function (svg, json) {
        console.log("json", json);
        if (json.result == 404) {
            alert(json.message);
            return true;
        };
        svg.graph.clear();

        var nodes = json.V.reduce((acc, current, index) => {
            node = {};
            node.id = current;
            node.label = 'Node ' + current;
            node.x = Math.random();
            node.y = Math.random();
            node.size = json.neighbours[index].length;
            node.color = '#666';
            svg.graph.addNode(node);
            return node;
        }, [])

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

    // Function to reset the page
    dynamicGraph.reset = function reset() {
        var loading_btn = document.getElementById("loading_btn");
        var cancel_btn = document.getElementById("cancel_btn");
        var progress_wrapper = document.getElementById("progress_wrapper");
        var progress_status = document.getElementById("progress_status");
        // Hide the cancel button
        cancel_btn.classList.add("d-none");
        // Hide the loading button
        loading_btn.classList.add("d-none");
        // Hide the progress bar
        progress_wrapper.classList.add("d-none");
        // Reset the progress bar state
        progress.setAttribute("style", `width: 0%`);

    };

    // Function to show alerts
    dynamicGraph.show_alert = function show_alert(message, alert) {
      // Get a reference to the alert wrapper
      var alert_wrapper = document.getElementById("alert_wrapper");
      alert_wrapper.innerHTML = `
        <div id="alert" class="alert alert-${alert} alert-dismissible show" role="alert">
          <span>${message}</span>
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
      `
    };

})(jQuery);

/* main */
jQuery(function ($) {

    var progress = document.getElementById("progress");
    var progress_wrapper = document.getElementById("progress_wrapper");
    var progress_status = document.getElementById("progress_status");
    var loading_btn = document.getElementById("loading_btn");
    var cancel_btn = document.getElementById("cancel_btn");

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
        dynamicGraph.reset();
        $('.progress').css('display', 'block');
        event.preventDefault();

        var typeName = $graphTypeInput.val(),
            type = dynamicGraph.types[typeName],
            data = {}

        $.each(type["required"], function (i, id) {
            var $input = $("#" + id);
            data[$input.attr('name')] = $input.val();
        });

        dynamicGraph.request(svg, "new", Number(data['N']));

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

        if (Number(data['L']) < 50) {
            dynamicGraph.show_alert(`Numbers Of New Nodes Must Be Greater Than 50`, "warning");
            return;
        }

        dynamicGraph.request(svg, "add", Number(data['L']));

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

        $.ajax({
            url: "/delete",
            type: "POST",
            cache: false,
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (json) {
                dynamicGraph.plotGraph(svg, json);
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
