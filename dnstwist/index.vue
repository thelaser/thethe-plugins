<template>
  <v-layout row pt-2 wrap class="subheading">
    <template>

      <v-flex>

        <v-card>
          <v-card-title primary-title>
            <span class="subheading">List of results </span>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="text-xs-left">

            <v-flex>
              <li
                style="list-style-type: none;" 
                v-for="index in resource.results.length" :key="index">

                  <ul >
                    <h3 v-if="resource.results[index-1].fuzzer.includes('original')" style="color:#33cc33; padding-bottom: 10px;"> Original domain info</h3>
                    <h3 v-else style="color:#cc33ff;padding-bottom: 10px;"> Possible copy</h3>

                    <li 
                    style="list-style-type: none;" 
                    v-for="(val, key) in resource.results[index-1]" :key="key">
                      
                      <div style="color:#99ccff; font-size: 150%;" v-if="key=='domain-name'">
                        <v-label >{{ key.toUpperCase() }}:</v-label>
                          {{ val }} 
                      </div>

                      <div style="color:#9999ff; font-size: 120%;" v-else-if="key=='dns-a'">
                        <v-label >{{ key.toUpperCase() }}:</v-label>
                          {{ val }} 
                      </div>

                      <div v-else> 
                        <v-label >{{ key.toUpperCase() }}:</v-label>
                          {{ val }} 
                      </div>
                    </li>
                  </ul>

                  <br>
                  <hr>
                  <br>
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
  name: "dnstwist",
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