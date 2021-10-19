<template>
  <v-layout row pt-2 wrap class="subheading">
    <template v-if="resource.results.seen">

      <v-flex>
        <v-card>
          <v-card-title primary-title>
            <span class="subheading">General info for {{ resource.results.ip }}</span>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="text-xs-left">
            <v-flex>
              <v-label>Actor:</v-label>
              {{ resource.results.actor }}
            </v-flex>
            <v-flex>
              <v-label>Classification:</v-label>
                {{ resource.results.classification }}
            </v-flex>
            <v-flex>
              <v-label>CVE:</v-label>
                {{ resource.results.cve }}
            </v-flex>
            <v-flex>
              <v-label>First seen:</v-label>
                {{ resource.results.first_seen }}
            </v-flex>
            <v-flex>
              <v-label>Classification:</v-label>
                {{ resource.results.last_seen }}
            </v-flex>
            <v-flex>
              <v-label>Port:</v-label>
                {{ resource.results.raw_data.scan[0].port }} / {{ resource.results.raw_data.scan[0].protocol }}
            </v-flex>
            <v-flex>
              <v-label>Spoofable:</v-label>
                {{ resource.results.spoofable }}
            </v-flex>
            <v-flex>
              <v-label> Tags: </v-label>
              <li 
              style="list-style-type: none;" 
              v-for="tag in resource.results.tags" :key="tag">
                {{ tag }}
              </li>
            </v-flex>
            
          </v-card-text>
        </v-card>
      </v-flex>

      <v-flex>
        <v-card>
          <v-card-title primary-title>
            <span class="subheading">Metadata</span>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="text-xs-left">
            <v-flex>
              <v-label>ASN:</v-label>
              {{ resource.results.metadata.asn }}
            </v-flex>
            <v-flex>
              <v-label>Category:</v-label>
                {{ resource.results.metadata.category }}
            </v-flex>
            <v-flex>
              <v-label>City:</v-label>
                {{ resource.results.metadata.city }}
            </v-flex>
            <v-flex>
              <v-label>Region:</v-label>
                {{ resource.results.metadata.region }}
            </v-flex>
            <v-flex>
              <v-label>Contry code:</v-label>
                {{ resource.results.metadata.country_code }}
            </v-flex>
            <v-flex>
              <v-label>Organization:</v-label>
                {{ resource.results.metadata.organization }}
            </v-flex>
            <v-flex>
              <v-label>OS:</v-label>
                {{ resource.results.metadata.os }}
            </v-flex>
            <v-flex>
              <v-label>RDNS:</v-label>
                {{ resource.results.metadata.rdns }}
            </v-flex>
            <v-flex>
              <v-label>TOR exit node:</v-label>
                {{ resource.results.metadata.tor }}
            </v-flex>
            
          </v-card-text>
        </v-card>
      </v-flex>

      <v-flex>
        <v-card>
          <v-card-title primary-title>
            <span class="subheading">Specific data</span>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="text-xs-left">
            <v-flex>
              <v-label>SSH data:</v-label>
              {{ resource.results.raw_data.hassh }}
            </v-flex>
            <v-flex>
              <v-label>JA3 data:</v-label>
                {{ resource.results.raw_data.ja3 }}
            </v-flex>
            <v-flex>
              <v-label>Web data:</v-label>
                {{ resource.results.raw_data.web }}
            </v-flex>
            <v-flex>
              <v-label>VPN IP:</v-label>
                {{ resource.results.vpn }}
            </v-flex>
            <v-flex>
              <v-label>VPN service:</v-label>
                {{ resource.results.vpn_service }}
            </v-flex>
            
          </v-card-text>
        </v-card>
      </v-flex>

    </template>
    <template v-else-if="!resource.results.seen">

      <v-flex>
        <v-card>
          <h2> IP {{ resource.results.ip }} has not been seen by GreyNoise </h2>
        </v-card>
      </v-flex>

    </template>
    <template v-else>
      <v-flex>Something went wrong!</v-flex>
    </template>
  </v-layout>
</template>

<script>
import { make_unique_list, from_python_time } from "../../../utils/utils";
import { mapActions, mapState } from "vuex";

export default {
  name: "greynoise",
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
