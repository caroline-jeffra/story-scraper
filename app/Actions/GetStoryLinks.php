<?php

namespace App\Actions;

use GuzzleHttp\Client;

class GetStoryLinks
{
    protected string $url;
    public function __construct(string $url)
    {
        $this->url = $url;
    }

    public function __invoke(): array
    {
        return $this->handle();
    }

    public function handle(): array
    {
        $client = new Client();

        $response = $client->get($this->url);
        $html = $response->getBody()->getContents();

        // Parse HTML
        $dom = new \DOMDocument();
        libxml_use_internal_errors(true);
        $dom->loadHTML($html);
        libxml_clear_errors();

        $xpath = new \DOMXPath($dom);

        $links = [];
        foreach ($xpath->query('//div[contains(@class,"continue-reading")]//a[@href]') as $a) {
            $links[] = $a->getAttribute('href');
        }

        return $links;
    }
}
