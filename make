#!/bin/bash

apt install jq -y
# Your Cloudflare details
zone_id="919418af68c3d817afeef7606dace180"
api_token="FlNUa3JMcG831nfxK5bl-6xbk39WO2HVW_K7x9Fi"
record_name="ap-srv.us.kg"  # Adjust if needed
ttl=120  # Time to live, can be set to any value you want

# Fetch the IPv4 address
ipv4=$(curl -s ifconfig.io -4)

# Replace '.' with '-'
ipv4_dash=$(echo "$ipv4" | tr '.' '-')

# Format the subdomain as x-x-x-x.ap-srv.us.kg
formatted_ip="${ipv4_dash}.${record_name}"

# Get the record ID for the DNS entry (replace with your domain name if necessary)
record_id=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records?name=$formatted_ip" \
     -H "Authorization: Bearer $api_token" \
     -H "Content-Type: application/json" | jq -r '.result[0].id')

# Check if the record exists, if not create a new one
if [ "$record_id" == "null" ]; then
    # Create the DNS record
    response=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records" \
         -H "Authorization: Bearer $api_token" \
         -H "Content-Type: application/json" \
         --data "{\"type\":\"A\",\"name\":\"$formatted_ip\",\"content\":\"$ipv4\",\"ttl\":$ttl,\"proxied\":false}")
else
    # Update the existing DNS record
    response=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records/$record_id" \
         -H "Authorization: Bearer $api_token" \
         -H "Content-Type: application/json" \
         --data "{\"type\":\"A\",\"name\":\"$formatted_ip\",\"content\":\"$ipv4\",\"ttl\":$ttl,\"proxied\":false}")
fi

# Check if the response was successful
if echo "$response" | grep -q '"success":true'; then
    echo "$formatted_ip was assigned"
else
    echo "Failed to update DNS record."
    echo "Response: $response"
fi
