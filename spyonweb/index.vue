<template>
  <v-layout row pt-2 wrap class="subheading">
    <template v-if="resource.results.status">

      <v-flex>
        <v-card>
          <v-card-title primary-title>
            <span style="font-size: 120%" class="subheading">Related domains to the target</span>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="text-xs-left">

            <v-flex>
              
              <li 
                style="list-style-type: none;" 
                v-for="(val, key) in resource.results.ips" :key="key">
                  <b style= "color:#9999ff; padding-bottom: 20%"> {{ key.replace(/__/g,".") }} :  </b>

                  <br>

                  <ul>
                    <li 
                        style="list-style-type: none;font-size: 120%;padding-bottom: 5px;" 
                        v-for="(domainreg, domain) in val.items" :key="domain">
                      <b>{{ domain.replace(/__/g,".") }}</b> registered on the <b>{{ domainreg.replace(/__/g,".") }}</b>
                    </li>
                  </ul>


              </li>

            </v-flex>
            
            
          </v-card-text>
        </v-card>
      </v-flex>

      

    </template>

    <template v-else>

      <v-flex>
        <v-card>
          <h2> There aren't associated domains! </h2>
        </v-card>
      </v-flex>

    </template>



  </v-layout>
</template>

<script>
import { make_unique_list, from_python_time, demongify_contents } from "../../../utils/utils";
import { mapActions, mapState } from "vuex";

export default {
  name: "spyonweb",
  props: {
    plugin_data: Object
  },
  data: function() {
    return {};
  },
  computed: {
    resource: function() {
      let plugin_result = { ...this.plugin_data };
      console.log(plugin_result);
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
    let results = demongify_contents(this.resource.results);
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