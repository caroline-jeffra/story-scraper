<?php

namespace App\Actions;

use GuzzleHttp\Client;

class GetStoryData
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

    private function handle(): array
    {
        $client = new Client();
        $response = $client->get($this->url);
        $html = $response->getBody()->getContents();

        $dom = new \DOMDocument();
        libxml_use_internal_errors(true);
        $dom->loadHTML($html);
        libxml_clear_errors();

        $xpath = new \DOMXPath($dom);

        $metadataNode = $xpath->query("//div[contains(@class, 'post-title')]")->item(0);
        $metadata = $metadataNode ? trim($metadataNode->textContent) : '';
        $splitMetadata = explode('Issue', $metadata);
        $issueData = trim(array_pop($splitMetadata));
        $issueParts = explode(',', $issueData);
        $issueNum = trim(array_shift($issueParts));

        $dateString = trim(implode($issueParts));
        $date = \DateTime::createFromFormat('F j Y', $dateString);

        $joinedMetadata = implode($splitMetadata);
        $resplitMetadata = explode('By', $joinedMetadata);

        $postAuthor = trim(array_pop($resplitMetadata));
        $postTitle = trim(implode($resplitMetadata));

        // Extract bcs-story-content (entire text inside .bcs-story-content)
        $storyContentNode = $xpath->query("//div[contains(@class, 'bcs-story-content')]")->item(0);
        $storyContent = $storyContentNode ? trim($storyContentNode->textContent) : '';

        return [
            'post-title' => $postTitle,
            'post-author' => $postAuthor,
            'issue-number' => $issueNum,
            'issue-date' => $date,
            'url' => $this->url,
            'bcs-story-content' => $storyContent,
        ];
    }
}
