<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Issue extends Model
{
    protected $table = 'issue';

    protected $fillable = [
        'issue_number',
        'publication_date',
    ];

    public function story(): HasMany
    {
        return $this->hasMany(Story::class, 'story_id');
    }
}
