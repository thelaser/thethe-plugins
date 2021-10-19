<template>
  <v-layout row pt-2 wrap class="subheading">
    <template>

      <v-flex>
        <v-card>
          <v-card-title primary-title>
            <span class="subheading">Results for IP {{ resource.results.ip }}</span>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="text-xs-left">

            <v-flex>

              <li 
                style="list-style-type: none;" 
                v-for="(val, key) in resource.results" :key="key">
                  {{ key.toUpperCase() }} :
                  
                  <b v-if="val==false || val==true || key=='blocklists'"
                  v-bind:style= "[val==false ? {'color':'#33cc33'} : {'color':'#cc3333'}]" > 
                    {{ val }}  
                  </b>
                  <b v-else style="color:#9999ff;"> {{ val }}</b>
              </li>

            </v-flex>
            
            
          </v-card-text>
        </v-card>
      </v-flex>

      

    </template>
  </v-layout>
</template>

<script>
import { make_unique_list, from_python_time } from "../../../utils/utils";
import { mapActions, mapState } from "vuex";

export default {
  name: "neutrino",
  props: {
    plugin_data: Object
  },
  data: function() {
    return {};
  },
  computed: {
    resource: function() {
      let plugin_result = { ...this.plugin_data };
      return plugin_result;
    }
  },
  methods: {
    ...mapActions("results", { pushResult: "push" }),
    formatted_time: function(ts) {
      return from_python_time(ts);
    },
    copy_content: async function(data) {
      await navigator.clipboard.writeText(data);
    }
  },

  beforeMount: function() {
    let results = this.resource.results;
    let domains = [];
    let keys = ["act", "acth", "pas", "pash"];
    keys.map(k => {
      if (results.hasOwnProperty(k)) {
        domains.push(results[k].map(item => item.o));
      }
    });

    domains = domains.flat();

    if (domains.length === 0) {
      domains = "";
    } else {
      domains = JSON.stringify(domains.flat());
    }

    this.pushResult({
      // This this.$options.name serves to have the plugin name.
      name: this.$options.name,
      result: domains
    });

  }
};
</script>