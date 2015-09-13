{%import 'macros.t' as macros with context%}
== Libaudioverse  Node Reference

This section is an overview of all Libaudioverse nodes.

For binding-specific references, see the bindings themselves.
Python uses docstrings, for example.
Also see the Binding-specific Notes section of this documentation.

Usually, the names of  nodes can be inferred by mentally stripping the `Lav_OBJTYPE_` prefix from the identifying constant and looking for `suffix_object` or `SuffixObject` depending on the conventions of your language.
These transformations are done for you in this document, listed as Camelcase Identifier and underscore identifier, respectively.

For a discussion of property types, see Property Types.  For a discussion of callbacksk see Callbacks.  This document is focused only on the  nodes themselves.

Any function not described in the <<c-api,C API section>> is a "extra function", a function which breaks the usual property model.
Extra functions do any number of things and are documented with the node that they manipulate.

To determine the number of inputs and outputs a node has, as well as their channel counts, check the general description of the node and the description of its constructor in that order.
No node's output or input count can change after the node is created.
A few nodes make the input and output channel counts change depending on properties.
The most notable node of this type is the amplitude panner.

{%for node_name in sorted_nodes%}
{%set node = nodes[node_name]%}
{%set doc_header = (node['doc_name']+" node") | title%}
[[node-{{node_name}}]]
=== {{doc_header}}

C Type Identifier: `{{node_name}}`

{%if node_name != "Lav_OBJTYPE_GENERIC_NODE"%}
Constructor: `{{functions[node['constructor']]|function_to_string}}`

{%if not node['inputs']%}
This node has no inputs.
{%elif node['inputs'] == "constructor"%}
The number of inputs to this node depends on parameters to its constructor.
{%elif node['inputs'] == "described"%}
The number of inputs to this node is described below.
{%else%}
[caption=""]
.Inputs
|====
|Index | Channels | Description
{%for info in node['inputs']%}
{%if info[0] == "dynamic"%}
|{{loop.index0}} |{{info[1]}} |{{info[2]}}
{%elif info[0] == "constructor"%}
|{{loop.index0}} |The number of channels for this input depends on parameters to this node's constructor. |{{info[1]}}
{%else%}
|{{loop.index0}} |{{info[0]}} |{{info[1]}}
{%endif%}
{%endfor%}
|====
{%endif%}

{%if not node['outputs']%}
This node has no outputs.
{%elif node['outputs'] == "constructor"%}
The number of outputs from this node depends on parameters to its constructor.
{%elif node['outputs'] == "described"%}
The outputs of this node are described below.
{%else%}
[caption=""]
.Outputs
|====
|Index | Channels | Description
{%for info in node['outputs']%}
{%if info[0] == "dynamic"%}
|{{loop.index0}} |{{info[1]}} |{{info[2]}}
{%elif info[0] == "constructor"%}
|{{loop.index0}} |The number of channels for this input depends on parameters to this node's constructor. |{{info[1]}}
{%else%}
|{{loop.index0}} |{{info[0]}} |{{info[1]}}
{%endif%}
{%endfor%}
|====
{%endif%}

{%endif%}

{{nodes[node_name]['doc_description']}}

{%if nodes[node_name]['has_properties']%}
==== Properties


{%for propinfo in nodes[node_name]['properties'].iteritems()%}

===== {{propinfo[1]['name']}}

C Enumeration Value: {{propinfo[0]}}

Type: {{propinfo[1]['type']}}

{%if propinfo[1]['type'] in ["int", "float", "double"]%}
Range: {%if 'value_enum' in propinfo[1]-%}
A value from the `{{propinfo[1]['value_enum']}}` enumeration.
{%else-%}
{{propinfo[1].get('range', '')}}
{%endif%}
{%endif%}

Default Value: {{propinfo[1].get('default', 'See Description')}}

{{propinfo[1]['doc_description']}}

{%endfor%}


{%endif%}
{%if nodes[node_name]['has_events']%}
==== Events

{%for callinfo in nodes[node_name]['events'].iteritems()%}

===== {{callinfo[1]['name']}}
C Enumeration Value: {{callinfo[0]}}

{{callinfo[1]['doc_description']}}

{%endfor%}

{%endif%}

{%if node['has_callbacks']%}
==== Callbacks

{%for name, info in node['callbacks'].iteritems()%}
===== {{name}}
Setter: {{functions[info['setter_name']]|function_to_string}}

Callback Prototype: {{info['callback_func']|function_to_string}}

{{macros.render_args_table("Callback Parameters", info['callback_func'], info['params'])}}

{{info['doc_description']}}
{%endfor%}
{%endif%}

{%if node['has_extra_functions']%}
==== Extra Functions

{%for c_name, info in node['extra_functions'].iteritems()%}
{{macros.render_function(c_name, info)}}

{%endfor%}
{%endif%}
{%endfor%}